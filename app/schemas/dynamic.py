from pydantic import create_model, EmailStr, field_validator
from typing import Any, Dict, Type

TYPE_MAP = {
            "str": str,
            "string": str,
            "email": EmailStr,
            "text": str,
            "int": int,
            "bool": bool
        }

class SchemaFactory:
    @staticmethod
    def create_v_model(name: str, fields_config: dict) -> Type:

        definitions = {}
        for field_name, field_type in fields_config.items():
            raw_type = field_type.get("type", "str")
            python_type = TYPE_MAP.get(raw_type, str)

            default_value = ... if field_type.get("required") else None
            definitions[field_name] = (python_type, default_value)

        def check_honeypot(cls, v):
            if v:
                raise ValueError("Spam detected")
            return v

        model = create_model(
            name,
            **definitions,
            __validators__={
                "check_honeypot": field_validator("confirm_email")(check_honeypot)
            }
        )

        return model