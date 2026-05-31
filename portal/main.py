from __future__ import annotations

import hashlib
import hmac
import importlib.util
import json
import os
import base64
import re
import secrets
import sys
import traceback
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import Body, Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


ROOT_DIR = Path(__file__).resolve().parents[1]
PORTAL_DIR = Path(__file__).resolve().parent
PORTAL_STATIC_DIR = PORTAL_DIR / "static"
GENERATED_DIR = PORTAL_DIR / "generated"
TECH_CARD_IMAGE_DIR = GENERATED_DIR / "tech-card-images"

BECK_DIR = ROOT_DIR / "beck"
EXPERT_DIR = ROOT_DIR / "shov_viewer"
EXPERT_PY_DIR = EXPERT_DIR / "py"
FRONT_DIST_DIR = ROOT_DIR / "front" / "dist"
TECHCARD_RES_DIR = BECK_DIR / "res"
TECHCARD_DB_DSN = "host=localhost port=5432 dbname=victor_2 user=postgres password=admin"
AUTH_DB_DSN = os.getenv("AUTH_DB_DSN", TECHCARD_DB_DSN)

for module_dir in (str(BECK_DIR), str(EXPERT_PY_DIR)):
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)


SESSION_COOKIE = "nk_session"
SESSION_DAYS = 7
PBKDF2_ITERATIONS = 260_000
DATA_URL_RE = re.compile(r"^data:(?P<mime>[-\w.]+/[-\w.+]+);base64,(?P<data>.+)$", re.DOTALL)


class AuthPayload(BaseModel):
    username: str
    password: str
    full_name: str | None = None
    position: str | None = None
    company: str | None = None


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


def db_connect():
    return psycopg2.connect(AUTH_DB_DSN, cursor_factory=RealDictCursor)


def init_auth_db() -> None:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    TECH_CARD_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    with db_connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS public.users (
                    id bigserial PRIMARY KEY,
                    username text NOT NULL UNIQUE,
                    password_hash text NOT NULL,
                    salt text NOT NULL,
                    full_name text NOT NULL DEFAULT '',
                    position text NOT NULL DEFAULT '',
                    company text NOT NULL DEFAULT '',
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    updated_at timestamp with time zone NOT NULL DEFAULT now()
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS public.sessions (
                    token text PRIMARY KEY,
                    user_id bigint NOT NULL,
                    expires_at timestamp with time zone NOT NULL,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT sessions_user_id_fkey
                        FOREIGN KEY (user_id)
                        REFERENCES public.users (id)
                        ON DELETE CASCADE
                )
                """
            )
            cursor.execute("ALTER TABLE public.users ADD COLUMN IF NOT EXISTS full_name text NOT NULL DEFAULT ''")
            cursor.execute("ALTER TABLE public.users ADD COLUMN IF NOT EXISTS position text NOT NULL DEFAULT ''")
            cursor.execute("ALTER TABLE public.users ADD COLUMN IF NOT EXISTS company text NOT NULL DEFAULT ''")
            cursor.execute("ALTER TABLE public.users ADD COLUMN IF NOT EXISTS updated_at timestamp with time zone NOT NULL DEFAULT now()")
            cursor.execute("ALTER TABLE IF EXISTS public.tech_cards ADD COLUMN IF NOT EXISTS user_id bigint")
            cursor.execute(
                """
                DO $$
                BEGIN
                    IF to_regclass('public.tech_cards') IS NOT NULL AND NOT EXISTS (
                        SELECT 1 FROM pg_constraint WHERE conname = 'tech_cards_user_id_fkey'
                    ) THEN
                        ALTER TABLE public.tech_cards
                        ADD CONSTRAINT tech_cards_user_id_fkey
                            FOREIGN KEY (user_id)
                            REFERENCES public.users (id)
                            ON DELETE SET NULL;
                    END IF;
                END $$;
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS public.tech_card_images (
                    id bigserial PRIMARY KEY,
                    tech_card_id bigint NOT NULL REFERENCES public.tech_cards (id) ON DELETE CASCADE,
                    image_url text NOT NULL,
                    created_at timestamp with time zone NOT NULL DEFAULT now()
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS public.tech_card_image_descriptions (
                    id bigserial PRIMARY KEY,
                    image_id bigint NOT NULL REFERENCES public.tech_card_images (id) ON DELETE CASCADE,
                    user_id bigint REFERENCES public.users (id) ON DELETE SET NULL,
                    description text NOT NULL,
                    is_ai_generated boolean NOT NULL DEFAULT false,
                    created_at timestamp with time zone NOT NULL DEFAULT now()
                )
                """
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS sessions_user_id_idx ON public.sessions (user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS sessions_expires_at_idx ON public.sessions (expires_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS tech_cards_user_id_idx ON public.tech_cards (user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS tech_card_images_tech_card_id_idx ON public.tech_card_images (tech_card_id)")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS tech_card_images_card_url_idx ON public.tech_card_images (tech_card_id, image_url)")
            cursor.execute("CREATE INDEX IF NOT EXISTS tech_card_image_descriptions_image_id_idx ON public.tech_card_image_descriptions (image_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS tech_card_image_descriptions_user_id_idx ON public.tech_card_image_descriptions (user_id)")
            cursor.execute(
                "DELETE FROM public.sessions WHERE expires_at <= %s",
                (utc_now(),),
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
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO public.sessions (token, user_id, expires_at, created_at)
                VALUES (%s, %s, %s, %s)
                """,
                (token, user_id, expires_at, utc_now()),
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
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM public.sessions WHERE token = %s", (token,))
    response.delete_cookie(SESSION_COOKIE)


def get_user_by_session_token(token: str | None) -> dict[str, Any] | None:
    if not token:
        return None

    now = utc_now()
    with db_connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT u.id, u.username, u.full_name, u.position, u.company
                FROM public.sessions s
                INNER JOIN public.users u ON u.id = s.user_id
                WHERE s.token = %s AND s.expires_at > %s
                LIMIT 1
                """,
                (token, now),
            )
            row = cursor.fetchone()

    return row if row else None


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
    full_name = (payload.full_name or "").strip()
    position = (payload.position or "").strip()
    company = (payload.company or "").strip()

    if len(username) < 3:
        raise HTTPException(status_code=400, detail="\u041b\u043e\u0433\u0438\u043d \u0434\u043e\u043b\u0436\u0435\u043d \u0431\u044b\u0442\u044c \u043d\u0435 \u043a\u043e\u0440\u043e\u0447\u0435 3 \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="\u041f\u0430\u0440\u043e\u043b\u044c \u0434\u043e\u043b\u0436\u0435\u043d \u0431\u044b\u0442\u044c \u043d\u0435 \u043a\u043e\u0440\u043e\u0447\u0435 6 \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432")
    if not full_name:
        raise HTTPException(status_code=400, detail="\u0423\u043a\u0430\u0436\u0438\u0442\u0435 \u0424\u0418\u041e")
    if not position:
        raise HTTPException(status_code=400, detail="\u0423\u043a\u0430\u0436\u0438\u0442\u0435 \u0434\u043e\u043b\u0436\u043d\u043e\u0441\u0442\u044c")
    if not company:
        raise HTTPException(status_code=400, detail="\u0423\u043a\u0430\u0436\u0438\u0442\u0435 \u043a\u043e\u043c\u043f\u0430\u043d\u0438\u044e")

    password_hash, salt = create_password_hash(password)
    try:
        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO public.users (
                        username,
                        password_hash,
                        salt,
                        full_name,
                        position,
                        company,
                        created_at,
                        updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (username, password_hash, salt, full_name, position, company, utc_now(), utc_now()),
                )
                row = cursor.fetchone()
                user_id = int(row["id"])
    except psycopg2.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u0443\u0436\u0435 \u0441\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u0435\u0442") from exc

    create_session(user_id, response)
    return {
        "username": username,
        "full_name": full_name,
        "position": position,
        "company": company,
    }


@app.post("/api/auth/login")
def login(payload: AuthPayload, response: Response) -> dict[str, Any]:
    username = normalize_username(payload.username)
    with db_connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, password_hash, salt, full_name, position, company
                FROM public.users
                WHERE username = %s
                LIMIT 1
                """,
                (username,),
            )
            row = cursor.fetchone()

    if not row or not verify_password(payload.password, row["password_hash"], row["salt"]):
        raise HTTPException(status_code=401, detail="\u041d\u0435\u0432\u0435\u0440\u043d\u044b\u0439 \u043b\u043e\u0433\u0438\u043d \u0438\u043b\u0438 \u043f\u0430\u0440\u043e\u043b\u044c")

    create_session(int(row["id"]), response)
    return {
        "username": row["username"],
        "full_name": row.get("full_name", ""),
        "position": row.get("position", ""),
        "company": row.get("company", ""),
    }


@app.post("/api/auth/logout")
def logout(request: Request, response: Response) -> dict[str, str]:
    clear_session(response, request.cookies.get(SESSION_COOKIE))
    return {"status": "ok"}


@app.get("/api/auth/me")
def me(user: dict[str, Any] = Depends(require_user)) -> dict[str, Any]:
    return {
        "username": user["username"],
        "full_name": user.get("full_name", ""),
        "position": user.get("position", ""),
        "company": user.get("company", ""),
    }


GENERATED_DIR.mkdir(parents=True, exist_ok=True)
TECH_CARD_IMAGE_DIR.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_tech_controller():
    from controllers.controllerWeb import ControllerWeb
    from repositories.postgresDataBase import PostgresDataBase
    from services.Changers.ch_ControlMethodsFromDb import ControlMethodsFromDb
    from services.Changers.ch_ControlSchemesFromDb import ControlSchemesFromJointTypeDb
    from services.Changers.ch_ControlSensitivity import ControlSensitivityChanger
    from services.Changers.ch_ControlledZoneWidthStub import ControlledZoneWidthStub
    from services.Changers.ch_CircButtWeldBeadFromThicknessTable import (
        CircButtWeldBeadFromThicknessTable,
    )
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
    pipe_line.addChanger(CircButtWeldBeadFromThicknessTable(), 0)
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


def get_image_extension(mime_type: str) -> str:
    return {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
        "image/bmp": ".bmp",
    }.get(mime_type.lower(), ".png")


def persist_data_url_image(image: dict[str, Any], card_slug: str, scope: str) -> dict[str, Any]:
    preview = image.get("preview")
    if not isinstance(preview, str):
        return image

    match = DATA_URL_RE.match(preview)
    if not match:
        return image

    mime_type = match.group("mime")
    extension = get_image_extension(mime_type)
    filename = f"{card_slug}_{scope}_{secrets.token_hex(8)}{extension}"
    filepath = TECH_CARD_IMAGE_DIR / filename

    try:
        filepath.write_bytes(base64.b64decode(match.group("data"), validate=True))
    except (ValueError, base64.binascii.Error) as exc:
        raise HTTPException(status_code=400, detail="Invalid image payload") from exc

    saved_image = dict(image)
    saved_image.pop("preview", None)
    saved_image["fileName"] = filename
    saved_image["preview"] = f"/tech-card-images/{filename}"
    saved_image["mimeType"] = mime_type
    return saved_image


def collect_tech_card_image_urls(snapshot: Any) -> list[str]:
    if not isinstance(snapshot, dict):
        return []

    urls: list[str] = []

    uploaded_images = snapshot.get("uploadedImages")
    if isinstance(uploaded_images, dict):
        for images in uploaded_images.values():
            if isinstance(images, list):
                for image in images:
                    if isinstance(image, dict) and isinstance(image.get("preview"), str):
                        urls.append(image["preview"])

    overview = snapshot.get("overview")
    if isinstance(overview, dict) and isinstance(overview.get("weldImages"), list):
        for image in overview["weldImages"]:
            if isinstance(image, dict) and isinstance(image.get("preview"), str):
                urls.append(image["preview"])

    return list(dict.fromkeys(urls))


def sync_tech_card_image_rows(card_id: int, image_urls: list[str]) -> None:
    with db_connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM public.tech_card_images WHERE tech_card_id = %s AND image_url <> ALL(%s)",
                (card_id, image_urls or [""]),
            )
            for image_url in image_urls:
                cursor.execute(
                    """
                    INSERT INTO public.tech_card_images (tech_card_id, image_url)
                    VALUES (%s, %s)
                    ON CONFLICT (tech_card_id, image_url) DO NOTHING
                    """,
                    (card_id, image_url),
                )


def persist_images_map(images_by_key: Any, card_slug: str, scope_prefix: str) -> dict[str, Any]:
    if not isinstance(images_by_key, dict):
        return {}

    result: dict[str, Any] = {}
    for key, images in images_by_key.items():
        if not isinstance(images, list):
            continue
        saved_images = []
        for index, image in enumerate(images):
            if isinstance(image, dict):
                saved_images.append(persist_data_url_image(image, card_slug, f"{scope_prefix}-{key}-{index}"))
        if saved_images:
            result[str(key)] = saved_images
    return result


def prepare_tech_card_snapshot_for_save(snapshot: Any, card_id: Any = None) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        return {}

    card_slug = str(card_id or secrets.token_hex(6))
    prepared = dict(snapshot)
    prepared["uploadedImages"] = persist_images_map(
        prepared.get("uploadedImages", {}),
        card_slug,
        "block",
    )

    overview = prepared.get("overview")
    if isinstance(overview, dict):
        prepared_overview = dict(overview)
        prepared_overview["weldImages"] = persist_images_map(
            {"overview": prepared_overview.get("weldImages", [])},
            card_slug,
            "overview",
        ).get("overview", [])
        prepared["overview"] = prepared_overview

    return prepared


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
            prepared_data = prepare_tech_card_snapshot_for_save(
                request_payload.get("data", {}),
                request_payload.get("id"),
            )
            tech_card = controller.saveTechCard(
                request_payload.get("name", ""),
                prepared_data,
                request_payload.get("id"),
                _user.get("id"),
            )
            saved_card_id = safe_int(tech_card.get("id") if isinstance(tech_card, dict) else None, 0)
            if saved_card_id > 0:
                sync_tech_card_image_rows(saved_card_id, collect_tech_card_image_urls(prepared_data))
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
app.mount("/tech-card-images", StaticFiles(directory=str(TECH_CARD_IMAGE_DIR)), name="tech-card-images")

if FRONT_DIST_DIR.exists():
    app.mount("/tech-cards", StaticFiles(directory=str(FRONT_DIST_DIR), html=True), name="tech-cards")
    front_assets_dir = FRONT_DIST_DIR / "assets"
    if front_assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(front_assets_dir)), name="tech-card-assets")

if TECHCARD_RES_DIR.exists():
    app.mount("/res", StaticFiles(directory=str(TECHCARD_RES_DIR)), name="tech-card-res")

if EXPERT_DIR.exists():
    app.mount("/expert-analysis", StaticFiles(directory=str(EXPERT_DIR), html=True), name="expert-analysis")
