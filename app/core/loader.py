import json
import os
from typing import Optional, Dict


class ConfigLoader:
    def __init__(self, data_path: str = "data"):
        self.data_path = data_path

    def get_client_config(self, client_id: str) -> Optional[Dict]:
        file_path = os.path.join(self.data_path, f"{client_id}.json")
        if not os.path.exists(file_path):
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)