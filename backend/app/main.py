from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.routes import checker

app = FastAPI(title="Label Check API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(checker.router)

@app.get("/")
async def root():
    return {
        "name": "Label Check API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
