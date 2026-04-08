from fastapi import APIRouter, Request, Depends, HTTPException

from app.core.dependencies import get_client_config
from app.core.loader import ConfigLoader
from app.core.engine import SynapseEngine
from app.schemas.dynamic import SchemaFactory

router = APIRouter()
engine = SynapseEngine()
loader = ConfigLoader()


@router.get("/schema")
async def get_form_schema(
        config: dict = Depends(get_client_config)
):
    return {
        "title": config.get("form_name"),
        "fields": config.get("fields")
    }


@router.post("/signal")
async def receive_signal(
        request: Request,
        config: dict = Depends(get_client_config)
):

    raw_data = await request.json()

    fields_config = config["fields"]
    DynamicModel = SchemaFactory.create_v_model("FormModel", fields_config)

    try:
        instance = DynamicModel(**raw_data)
        validated_dict = instance.model_dump()
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    try:
        results = await engine.run_flow(
            flow_config=config.get("flow", []),
            data=validated_dict,
            context={"client_id": config["client_id"]}
        )

        return {
            "status": "success",
            "actions_executed": results
        }

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal engine error: {str(e)}"
        )