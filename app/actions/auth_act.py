# app/actions/auth_act.py
import logging
from fastapi import HTTPException
from app.actions.base import BaseAction
from app.core.auth import create_access_token, verify_password

logger = logging.getLogger("uvicorn.error")


class AuthCheckAction(BaseAction):
    async def execute(self, data: dict, params: dict) -> dict:

        user_password = data.get("password")

        required_hash = params.get("secret_hash")

        if not required_hash:
            logger.error("AuthCheckAction: secret_hash is missing in config")
            return {"status": "error", "message": "Server error"}

        if verify_password(user_password, required_hash):
            token = create_access_token(data={
                "client_id": data.get("client_id"),
                "page": data.get("page")
            })

            return {
                "status": "success",
                "message": "Authorized",
                "action": "auth_check",
                "token": token,
            }

        raise HTTPException(
            status_code=401,
            detail="Invalid access password"
        )