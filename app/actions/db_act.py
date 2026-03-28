import json
import os
import logging
from datetime import datetime
from app.actions.base import BaseAction

STORAGE_PATH = "/app/data/storage"
logger = logging.getLogger("uvicorn.error")

class DbSaveAction(BaseAction):
    def __init__(self):

        if not os.path.exists(STORAGE_PATH):
            try:
                os.makedirs(STORAGE_PATH, exist_ok=True)
            except Exception as e:
                logger.error(f"Could not create storage directory: {e}")

    async def execute(self, data: dict, params: dict) -> dict:

        client_id = params.get("client_id", "unknown")
        file_path = os.path.join(STORAGE_PATH, f"storage_{client_id}.json")

        record = {
            "timestamp": datetime.now().isoformat(),
            "payload": data
        }

        try:
            storage_data = []

            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        storage_data = json.load(f)
                        if not isinstance(storage_data, list):
                            storage_data = []
                    except json.JSONDecodeError:
                        logger.warning(f"Corrupted JSON in {file_path}, starting fresh.")
                        storage_data = []

            storage_data.append(record)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(storage_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Signal saved to {file_path}. Total records: {len(storage_data)}")

            return {
                "status": "success",
                "action": "db_save",
                "file": file_path,
                "count": len(storage_data)
            }

        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
            return {"status": "error", "message": str(e)}