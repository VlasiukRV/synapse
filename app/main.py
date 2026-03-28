from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import router as api_v1_router

app = FastAPI()

origins = [
    "http://localhost:4321",
    "http://127.0.0.1:4321",
    "http://192.168.4.25:8098",

    "https://tsb-enterprise.com",
    "https://www.tsb-enterprise.com",
    "https://uptarget-co.tsb-enterprise.com",
    "https://www.uptarget-co.tsb-enterprise.com"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/api/v1/synapse")