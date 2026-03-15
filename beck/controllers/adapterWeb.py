from fastapi import Body, FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from interfaces.i_controllers import IControllers
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from urllib.parse import quote

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
        try:
            methodology = payload.get("methodology", 0)
            if control_type == "object":
                tech_card = controller.getObjectControl(methodology)
            elif control_type == "element":
                tech_card = controller.getControlElements(payload.get("type", 1), methodology)
            elif control_type == "elementParams":
                tech_card = controller.getControlElementParam(payload.get("idElement", 1), methodology)
            elif control_type == "elementParamValue":
                tech_card = controller.getElementParamsValues(payload.get("idElement", 1), methodology)
            elif control_type == "updateTechCard":
                tech_card = controller.updateTechCard(payload.get("techCard", {}))
            elif control_type == "methodologies":
                methodologies = controller.getMethodologies()
                tech_card = {
                    "items": [
                        {"id": str(methodology_id), "name": methodology_name}
                        for methodology_id, methodology_name in methodologies.items()
                    ]
                }
            elif control_type == "createParamOption":
                tech_card = controller.createParamOption(payload)
            elif control_type == "exportTechCard":
                exported_file = controller.exportTechCard(payload)
                filename = exported_file.get("filename", "tech-card.docx")
                content_type = exported_file.get(
                    "content_type",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
                headers = {
                    "Content-Disposition": (
                        f"attachment; filename=\"tech-card.docx\"; "
                        f"filename*=UTF-8''{quote(filename)}"
                    )
                }
                return Response(
                    content=exported_file.get("content", b""),
                    media_type=content_type,
                    headers=headers,
                )
            else:
                return {}

            print(tech_card)
            if hasattr(tech_card, "serialise"):
                return tech_card.serialise()
            return tech_card
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    uvicorn.run(app, host="0.0.0.0", port=8000)
    return adapter

   # get_available_params_for_type
