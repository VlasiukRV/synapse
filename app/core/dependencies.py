import json
import os
import logging
from fastapi import Header, HTTPException

logger = logging.getLogger(__name__)

BASE_DIR = "/app"
DATA_PATH = os.path.join(BASE_DIR, "data")

class ConfigProvider:
    async def __call__(self,
                       x_client_id: str = Header(..., alias="X-Client-ID"),
                       form_name: str = "contact_form"):
        logger.log(level=1, msg=f"X-Client-ID: {x_client_id}")

        file_path = os.path.join(DATA_PATH, f"{x_client_id}.json")

        if not os.path.exists(file_path):
            logger.error(f"CONFIG NOT FOUND: Looking for {file_path}")
            raise HTTPException(status_code=404, detail="Client configuration not found")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                client_data = json.load(f)

                if isinstance(client_data, list):
                    form_config = next((f for f in client_data if f.get("form_name") == form_name), None)

                elif client_data.get("form_name") == form_name:
                    form_config = client_data
                else:
                    form_config = None

                if not form_config:
                    raise HTTPException(status_code=404, detail=f"Form '{form_name}' not found for client")

                form_config["client_id"] = x_client_id
                return form_config
        except json.JSONDecodeError:
            logger.error(f"INVALID JSON: {file_path}")
            raise HTTPException(status_code=500, detail="Config file has invalid JSON format")
        except Exception:
            logger.error(f"READ ERROR: {str(e)}")
            raise HTTPException(status_code=500, detail="Error reading configuration")


get_client_config = ConfigProvider()