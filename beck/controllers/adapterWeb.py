from fastapi import FastAPI, HTTPException,Request
from pydantic import BaseModel
from interfaces.i_controllers import IControllers
import uvicorn
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware

urlObjec="object"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для теста
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def create_adapter(controller: IControllers,):
    @app.post("/techcard/{control_type}")
    async def adapter(control_type: str,payload: dict = Body(...)):
        print("Запрос пришёл")
        try:
            if control_type == "object":
                tech_card = controller.getObjectControl()
            elif control_type == "element":
                tech_card = controller.getControlElements(payload.get("type", 1))
            elif control_type=="elementParams":
                tech_card = controller.getControlElementParam(payload.get("idElement", 1))
            elif control_type=="elementParamValue":
                tech_card = controller.getElementParamsValues(payload.get("idElement", 1))
            elif control_type=="updateTechCard":
                tech_card = controller.updateTechCard(payload.get("techCard", {}))
                
            else:
                return{}

            print(tech_card)
            return tech_card.serialise()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    uvicorn.run(app, host="0.0.0.0", port=8000)    
    return adapter

   # get_available_params_for_type