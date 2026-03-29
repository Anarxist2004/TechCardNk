import traceback

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from controllers.Interfaces.i_controllers import IControllers
import uvicorn
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

urlObjec = "object"

app = FastAPI()
res_dir = Path(__file__).resolve().parent.parent / "res"
if res_dir.exists():
    app.mount("/res", StaticFiles(directory=str(res_dir)), name="res")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для теста
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_adapter(controller: IControllers,):
    @app.post("/techcard/{control_type}")
    async def adapter(control_type: str, payload: dict = Body(...)):
        print("Запрос пришёл")
        request_payload = payload if isinstance(payload, dict) else {}

        def safe_int(value, default=0):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        methodology = safe_int(request_payload.get("methodology", 0), 0)
        element_id = safe_int(request_payload.get("idElement", 1), 1)
        element_type = safe_int(request_payload.get("type", 1), 1)
        try:
            if control_type == "template":
                tech_card = controller.get_template()
            elif control_type == "updateTechCard":
                tech_card = controller.updateTechCard(request_payload.get("techCard", {}))
            else:
                return {}

            print(tech_card)

            return tech_card
        except Exception as e:
            print(
                "[adapter] Request failed: "
                f"control_type={control_type}, methodology={methodology}, "
                f"idElement={element_id}, type={element_type}, "
                f"payload_keys={list(request_payload.keys())}. Error: {e}"
            )
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=(
                    f"{control_type} failed for methodology={methodology}, "
                    f"idElement={element_id}. See backend log for traceback."
                ),
            )

    uvicorn.run(app, host="0.0.0.0", port=8000)
    return adapter

   # get_available_params_for_type
