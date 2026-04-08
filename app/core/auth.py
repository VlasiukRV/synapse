# app/core/auth.py
import os
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

ALGORITHM = "HS256"
logger = logging.getLogger("uvicorn.error")

def get_secret_key():
    key = os.getenv("TOKEN_SECRET_KEY")
    if not key:
        raise RuntimeError("TOKEN_SECRET_KEY is missing in env")
    return key

def hash_password(password: str) -> str:
    salt = get_secret_key()
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=24)):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=24)

    to_encode.update({"exp": expire})

    try:
        encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to encode JWT: {e}")
        raise RuntimeError("Token generation failed")

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return {}