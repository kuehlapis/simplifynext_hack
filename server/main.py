from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from server.controller.upload_controller import router as ocr_router
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Planner Agent API"}
