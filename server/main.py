from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.controller.upload_controller import router as ocr_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(ocr_router)


@app.get("/")
async def read_root():
    return {"message": "gaytards"}
