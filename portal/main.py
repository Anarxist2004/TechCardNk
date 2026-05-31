from __future__ import annotations

import hashlib
import hmac
import importlib.util
import json
import os
import secrets
import sqlite3
import sys
import traceback
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import Body, Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


ROOT_DIR = Path(__file__).resolve().parents[1]
PORTAL_DIR = Path(__file__).resolve().parent
PORTAL_STATIC_DIR = PORTAL_DIR / "static"
AUTH_DB_PATH = PORTAL_DIR / "auth.sqlite3"
GENERATED_DIR = PORTAL_DIR / "generated"

BECK_DIR = ROOT_DIR / "beck"
EXPERT_DIR = ROOT_DIR / "shov_viewer"
EXPERT_PY_DIR = EXPERT_DIR / "py"
FRONT_DIST_DIR = ROOT_DIR / "front" / "dist"
TECHCARD_RES_DIR = BECK_DIR / "res"
TECHCARD_DB_DSN = "host=localhost port=5432 dbname=victor_2 user=postgres password=admin"

for module_dir in (str(BECK_DIR), str(EXPERT_PY_DIR)):
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)


SESSION_COOKIE = "nk_session"
SESSION_DAYS = 7
PBKDF2_ITERATIONS = 260_000


class AuthPayload(BaseModel):
    username: str
    password: str


app = FastAPI(title="NK unified service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def db_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(AUTH_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_auth_db() -> None:
    PORTAL_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    with db_connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            "DELETE FROM sessions WHERE expires_at <= ?",
            (utc_now().isoformat(),),
        )


@app.on_event("startup")
def startup() -> None:
    init_auth_db()


def normalize_username(username: str) -> str:
    return username.strip().lower()


def hash_password(password: str, salt_hex: str) -> str:
    salt = bytes.fromhex(salt_hex)
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    ).hex()


def create_password_hash(password: str) -> tuple[str, str]:
    salt_hex = secrets.token_hex(16)
    return hash_password(password, salt_hex), salt_hex


def verify_password(password: str, expected_hash: str, salt_hex: str) -> bool:
    actual_hash = hash_password(password, salt_hex)
    return hmac.compare_digest(actual_hash, expected_hash)


def create_session(user_id: int, response: Response) -> None:
    token = secrets.token_urlsafe(32)
    expires_at = utc_now() + timedelta(days=SESSION_DAYS)
    with db_connect() as conn:
        conn.execute(
            "INSERT INTO sessions (token, user_id, expires_at, created_at) VALUES (?, ?, ?, ?)",
            (token, user_id, expires_at.isoformat(), utc_now().isoformat()),
        )

    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=SESSION_DAYS * 24 * 60 * 60,
        httponly=True,
        samesite="lax",
    )


def clear_session(response: Response, token: str | None = None) -> None:
    if token:
        with db_connect() as conn:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    response.delete_cookie(SESSION_COOKIE)


def get_user_by_session_token(token: str | None) -> dict[str, Any] | None:
    if not token:
        return None

    now = utc_now().isoformat()
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT u.id, u.username
            FROM sessions s
            INNER JOIN users u ON u.id = s.user_id
            WHERE s.token = ? AND s.expires_at > ?
            LIMIT 1
            """,
            (token, now),
        ).fetchone()

    return dict(row) if row else None


def current_user(request: Request) -> dict[str, Any] | None:
    return get_user_by_session_token(request.cookies.get(SESSION_COOKIE))


def require_user(request: Request) -> dict[str, Any]:
    user = current_user(request)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def is_public_path(path: str) -> bool:
    return (
        path == "/"
        or path == "/favicon.ico"
        or path.startswith("/portal-static/")
        or path.startswith("/api/auth/")
        or path in {"/docs", "/openapi.json", "/redoc"}
    )


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if is_public_path(request.url.path):
        return await call_next(request)

    if current_user(request) is None:
        if (
            request.url.path.startswith("/api/")
            or request.url.path.startswith("/techcard")
            or request.url.path
            in {
                "/find_shov",
                "/save_annotation",
                "/download_annotation",
                "/save_protocol_docx",
            }
        ):
            return JSONResponse({"detail": "Authentication required"}, status_code=401)
        return RedirectResponse("/")

    return await call_next(request)


@app.get("/", response_class=HTMLResponse)
def portal_index() -> str:
    return (PORTAL_STATIC_DIR / "index.html").read_text(encoding="utf-8")


def inject_module_nav(html: str) -> str:
    if "/portal-static/module-nav.css" not in html:
        html = html.replace(
            "</head>",
            '    <link rel="stylesheet" href="/portal-static/module-nav.css" />\n</head>',
            1,
        )
    if "/portal-static/module-nav.js" not in html:
        html = html.replace(
            "</head>",
            '    <script src="/portal-static/module-nav.js" defer></script>\n</head>',
            1,
        )
    return html


@app.post("/api/auth/register")
def register(payload: AuthPayload, response: Response) -> dict[str, Any]:
    username = normalize_username(payload.username)
    password = payload.password

    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Логин должен быть не короче 3 символов")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Пароль должен быть не короче 6 символов")

    password_hash, salt = create_password_hash(password)
    try:
        with db_connect() as conn:
            cursor = conn.execute(
                "INSERT INTO users (username, password_hash, salt, created_at) VALUES (?, ?, ?, ?)",
                (username, password_hash, salt, utc_now().isoformat()),
            )
            user_id = int(cursor.lastrowid)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Пользователь уже существует") from exc

    create_session(user_id, response)
    return {"username": username}


@app.post("/api/auth/login")
def login(payload: AuthPayload, response: Response) -> dict[str, Any]:
    username = normalize_username(payload.username)
    with db_connect() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash, salt FROM users WHERE username = ? LIMIT 1",
            (username,),
        ).fetchone()

    if not row or not verify_password(payload.password, row["password_hash"], row["salt"]):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    create_session(int(row["id"]), response)
    return {"username": row["username"]}


@app.post("/api/auth/logout")
def logout(request: Request, response: Response) -> dict[str, str]:
    clear_session(response, request.cookies.get(SESSION_COOKIE))
    return {"status": "ok"}


@app.get("/api/auth/me")
def me(user: dict[str, Any] = Depends(require_user)) -> dict[str, Any]:
    return {"username": user["username"]}


@lru_cache(maxsize=1)
def get_tech_controller():
    from controllers.controllerWeb import ControllerWeb
    from repositories.postgresDataBase import PostgresDataBase
    from services.Changers.ch_ControlMethodsFromDb import ControlMethodsFromDb
    from services.Changers.ch_ControlSchemesFromDb import ControlSchemesFromJointTypeDb
    from services.Changers.ch_ControlSensitivity import ControlSensitivityChanger
    from services.Changers.ch_ControlledZoneWidthStub import ControlledZoneWidthStub
    from services.Changers.ch_IntensifyingScreenByVoltage import IntensifyingScreenByVoltage
    from services.Changers.ch_MaterialsFromDb import MaterialsFromDb
    from services.Changers.ch_ParamsByWeldedJointFromDb import ParamsByWeldedJointFromDb
    from services.Changers.ch_ProtectiveScreenByVoltage import ProtectiveScreenByVoltage
    from services.Changers.ch_RadiographicFilmFromDb import RadiographicFilmFromDb
    from services.Changers.ch_RectilinearDrDistance import RectilinearDrDistance
    from services.Changers.ch_RegulatoryDocumentsFromDb import RegulatoryDocumentsFromDb
    from services.Changers.ch_RengenApparatusForPanoramicScheme import (
        RengenApparatusForPanoramicScheme,
    )
    from services.Changers.ch_RengenApparatusFromDb import RengenApparatusFromDb
    from services.Changers.ch_RengenDistanceForDoubleWallScheme import (
        RengenDistanceForDoubleWallScheme,
    )
    from services.Changers.ch_RengenDistanceForEllipseFrontalScheme import (
        RengenDistanceForEllipseFrontalScheme,
    )
    from services.Changers.ch_SensitivityEtalonByMaterial import SensitivityEtalonByMaterial
    from services.Changers.ch_TypeOfWeldedJointFromDb import TypeOfWeldedJointFromDb
    from services.Changers.ch_WeldedJointDiagramFromDb import WeldedJointDiagramFromDb
    from services.PipeLine import PipeLine
    from services.tech_card_service import TechCardService

    repos = PostgresDataBase(TECHCARD_DB_DSN)
    pipe_line = PipeLine()
    pipe_line.addChanger(ControlMethodsFromDb(repos), 0)
    pipe_line.addChanger(RegulatoryDocumentsFromDb(repos), 0)
    pipe_line.addChanger(TypeOfWeldedJointFromDb(repos), 0)
    pipe_line.addChanger(WeldedJointDiagramFromDb(repos), 0)
    pipe_line.addChanger(ControlSchemesFromJointTypeDb(repos), 0)
    pipe_line.addChanger(MaterialsFromDb(repos), 0)
    pipe_line.addChanger(RengenApparatusFromDb(repos), 0)
    pipe_line.addChanger(ParamsByWeldedJointFromDb(repos), 0)
    pipe_line.addChanger(ControlSensitivityChanger(), 0)
    pipe_line.addChanger(RengenApparatusForPanoramicScheme(repos), 0)
    pipe_line.addChanger(RengenDistanceForDoubleWallScheme(), 0)
    pipe_line.addChanger(RengenDistanceForEllipseFrontalScheme(), 0)
    pipe_line.addChanger(RectilinearDrDistance(), 0)
    pipe_line.addChanger(SensitivityEtalonByMaterial(repos), 0)
    pipe_line.addChanger(RadiographicFilmFromDb(repos), 0)
    pipe_line.addChanger(IntensifyingScreenByVoltage(), 0)
    pipe_line.addChanger(ProtectiveScreenByVoltage(), 0)
    pipe_line.addChanger(ControlledZoneWidthStub(), 0)

    service = TechCardService(repos, pipe_line)
    return ControllerWeb(service)


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def serialize_techcard_response(value: Any) -> Any:
    serialise = getattr(value, "serialise", None)
    if callable(serialise):
        return serialise()
    return value


def extract_multipart_file(body: bytes, content_type: str) -> bytes:
    marker = "boundary="
    if marker not in content_type:
        raise HTTPException(status_code=400, detail="Multipart boundary is missing")

    boundary = content_type.split(marker, 1)[1].split(";", 1)[0].strip().strip('"')
    if not boundary:
        raise HTTPException(status_code=400, detail="Multipart boundary is empty")

    delimiter = f"--{boundary}".encode("utf-8")
    for raw_part in body.split(delimiter):
        part = raw_part.strip(b"\r\n")
        if not part or part == b"--" or b"\r\n\r\n" not in part:
            continue

        headers, payload = part.split(b"\r\n\r\n", 1)
        disposition = headers.decode("utf-8", errors="ignore").lower()
        if 'name="file"' not in disposition:
            continue

        if payload.endswith(b"\r\n--"):
            payload = payload[:-4]
        elif payload.endswith(b"\r\n"):
            payload = payload[:-2]

        if not payload:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        return payload

    raise HTTPException(status_code=400, detail="No file uploaded")


@app.post("/techcard/{control_type}")
async def techcard_adapter(
    control_type: str,
    payload: dict[str, Any] = Body({}),
    _user: dict[str, Any] = Depends(require_user),
):
    controller = get_tech_controller()
    request_payload = payload if isinstance(payload, dict) else {}
    methodology = safe_int(request_payload.get("methodology", 0), 0)
    element_id = safe_int(request_payload.get("idElement", 1), 1)

    try:
        if control_type == "template":
            tech_card = controller.get_template()
        elif control_type == "updateTechCard":
            tech_card = controller.updateTechCard(request_payload.get("techCard", {}))
        elif control_type == "saveTechCard":
            tech_card = controller.saveTechCard(
                request_payload.get("name", ""),
                request_payload.get("data", {}),
                request_payload.get("id"),
            )
        elif control_type == "listSavedTechCards":
            tech_card = controller.listSavedTechCards()
        elif control_type == "getSavedTechCard":
            card_id = safe_int(request_payload.get("id"), 0)
            tech_card = controller.getSavedTechCard(card_id)
            if tech_card is None:
                raise HTTPException(status_code=404, detail="Tech card not found")
        else:
            tech_card = {}

        return serialize_techcard_response(tech_card)
    except HTTPException:
        raise
    except Exception as exc:
        print(
            "[portal techcard] Request failed: "
            f"control_type={control_type}, methodology={methodology}, "
            f"idElement={element_id}, payload_keys={list(request_payload.keys())}. Error: {exc}"
        )
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{control_type} failed for methodology={methodology}, idElement={element_id}",
        ) from exc


@lru_cache(maxsize=1)
def get_expert_backend():
    spec = importlib.util.spec_from_file_location(
        "expert_backend",
        EXPERT_PY_DIR / "main.py",
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load expert backend")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@app.get("/download_annotation")
def download_annotation(_user: dict[str, Any] = Depends(require_user)):
    filepath = EXPERT_DIR / "annotations" / "annotation.json"
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=filepath,
        filename="annotation.json",
        media_type="application/json",
    )


@app.post("/find_shov")
async def find_shov(
    request: Request,
    _user: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    backend = get_expert_backend()
    filename = f"shov_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}.png"
    filepath = EXPERT_PY_DIR / filename
    file_bytes = extract_multipart_file(
        await request.body(),
        request.headers.get("content-type", ""),
    )

    with filepath.open("wb") as buffer:
        buffer.write(file_bytes)

    coords = backend.get_pic2(str(filepath), 2)
    return {
        "status": "success",
        "filename": filename,
        "path": str(filepath),
        "coordinates": coords,
    }


@app.post("/save_annotation")
async def save_annotation(
    request: Request,
    _user: dict[str, Any] = Depends(require_user),
) -> dict[str, str]:
    data = await request.json()
    annotations_dir = EXPERT_DIR / "annotations"
    annotations_dir.mkdir(parents=True, exist_ok=True)

    filepath = annotations_dir / "annotation.json"
    filepath.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {"status": "ok"}


@app.post("/save_protocol_docx")
async def save_protocol_docx(
    request: Request,
    _user: dict[str, Any] = Depends(require_user),
):
    data = await request.json()
    backend = get_expert_backend()
    template_path = EXPERT_PY_DIR / "protocol_docx.docx"
    if not template_path.exists():
        raise HTTPException(status_code=404, detail="Protocol template not found")

    previous_cwd = Path.cwd()
    try:
        os.chdir(EXPERT_PY_DIR)
        output = backend.protocol.build_protocol_doc(data, template_path)
    finally:
        os.chdir(previous_cwd)

    filepath = GENERATED_DIR / "protocol_generated.docx"
    filepath.write_bytes(output.getvalue())

    return FileResponse(
        path=filepath,
        filename="protocol.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@app.get("/tech-cards")
def tech_cards_redirect(_user: dict[str, Any] = Depends(require_user)):
    return RedirectResponse("/tech-cards/")


@app.get("/tech-cards/", response_class=HTMLResponse)
def tech_cards_index(_user: dict[str, Any] = Depends(require_user)) -> str:
    index_path = FRONT_DIST_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Tech cards frontend build not found")
    return inject_module_nav(index_path.read_text(encoding="utf-8"))


@app.get("/expert-analysis")
def expert_analysis_redirect(_user: dict[str, Any] = Depends(require_user)):
    return RedirectResponse("/expert-analysis/")


app.mount("/portal-static", StaticFiles(directory=str(PORTAL_STATIC_DIR)), name="portal-static")

if FRONT_DIST_DIR.exists():
    app.mount("/tech-cards", StaticFiles(directory=str(FRONT_DIST_DIR), html=True), name="tech-cards")
    front_assets_dir = FRONT_DIST_DIR / "assets"
    if front_assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(front_assets_dir)), name="tech-card-assets")

if TECHCARD_RES_DIR.exists():
    app.mount("/res", StaticFiles(directory=str(TECHCARD_RES_DIR)), name="tech-card-res")

if EXPERT_DIR.exists():
    app.mount("/expert-analysis", StaticFiles(directory=str(EXPERT_DIR), html=True), name="expert-analysis")
