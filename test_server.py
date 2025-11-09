#!/usr/bin/env python3
"""
Минимальный тест сервера для отладки проблем с endpoints
"""
import sys
import os
from pathlib import Path

# Добавляем пути
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Test API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Server is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/process/rus")
async def test_rus(
    schedule_file: UploadFile = File(...),
    report_file: UploadFile = File(...),
    max_shows: int = Form(3),
):
    return {
        "message": "RUS endpoint works!",
        "schedule_name": schedule_file.filename,
        "report_name": report_file.filename,
        "max_shows": max_shows
    }

@app.post("/api/process/foreign")
async def test_foreign(
    schedule_file: UploadFile = File(...),
    report_file: UploadFile = File(...),
    max_shows: int = Form(3),
):
    return {
        "message": "Foreign endpoint works!",
        "schedule_name": schedule_file.filename,
        "report_name": report_file.filename,
        "max_shows": max_shows
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting test server on http://localhost:8000")
    print("Test endpoints:")
    print("  GET  /health")
    print("  POST /api/process/rus")
    print("  POST /api/process/foreign")
    uvicorn.run(app, host="127.0.0.1", port=8000)
