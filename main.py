"""Food Verse AI - FastAPI backend (Epic 6). Run: uvicorn app.main:app --reload"""
from __future__ import annotations

import os
import tempfile
from dataclasses import asdict
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app import config
from app.modules.food_recognition.recognizer import FoodRecognizer
from app.modules.freshness.detector import FreshnessDetector
from app.modules.hygiene import monitor
from app.modules.kitchen import assistant
from app.modules.planner import meal_planner

app = FastAPI(
    title="Food Verse AI",
    version="0.1.0",
    description="Multimodal food intelligence: recognition, freshness, hygiene, cooking help, meal planning.",
)

recognizer = FoodRecognizer()
freshness = FreshnessDetector()


async def _read_limited(file: UploadFile) -> bytes:
    data = await file.read()
    if len(data) > config.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"File larger than {config.MAX_UPLOAD_MB} MB")
    if not data:
        raise HTTPException(400, "Empty file")
    return data


@app.get("/health")
def health():
    return {"status": "ok", "backend": config.BACKEND}


@app.post("/api/food/recognize")
async def recognize(file: UploadFile = File(...), grams: Optional[float] = Form(None), top_k: int = Form(3)):
    data = await _read_limited(file)
    try:
        return recognizer.recognize(data, grams=grams, top_k=top_k)
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception:
        raise HTTPException(400, "Could not read the image")


@app.post("/api/freshness/analyze")
async def analyze_freshness(file: UploadFile = File(...)):
    data = await _read_limited(file)
    try:
        return freshness.analyze(data)
    except Exception:
        raise HTTPException(400, "Could not read the image")


@app.post("/api/hygiene/analyze")
async def analyze_hygiene(
    file: UploadFile = File(...),
    every_seconds: float = Form(2.0),
    required: str = Form("gloves,hairnet,apron,mask"),
):
    data = await _read_limited(file)
    req = tuple(x.strip().lower() for x in required.split(",") if x.strip())
    suffix = os.path.splitext(file.filename or "")[1] or ".mp4"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:  # processed then discarded
        tmp.write(data)
        tmp.flush()
        try:
            report = monitor.analyze_video(tmp.name, required=req, every_seconds=every_seconds)
        except RuntimeError as e:
            raise HTTPException(503, str(e))
    return asdict(report)


class SuggestRequest(BaseModel):
    ingredients: list[str] = Field(min_length=1)
    limit: int = 5


class GuideRequest(BaseModel):
    dish: str
    servings: int = 2


@app.post("/api/kitchen/suggest")
def kitchen_suggest(req: SuggestRequest):
    return {"suggestions": assistant.suggest_recipes(req.ingredients, req.limit)}


@app.post("/api/kitchen/guide")
def kitchen_guide(req: GuideRequest):
    return assistant.guide(req.dish, req.servings)


class PlanRequest(BaseModel):
    age: int = Field(ge=14, le=100)
    sex: str = Field(pattern="^(male|female)$")
    height_cm: float = Field(gt=100, lt=250)
    weight_kg: float = Field(gt=30, lt=300)
    activity: str = "moderate"
    goal: str = Field("maintain", pattern="^(lose|maintain|gain)$")
    diet: list[str] = []
    allergies: list[str] = []


@app.post("/api/planner/generate")
def planner_generate(req: PlanRequest):
    if req.activity not in meal_planner.ACTIVITY:
        raise HTTPException(422, f"activity must be one of {list(meal_planner.ACTIVITY)}")
    return meal_planner.generate_plan(meal_planner.Profile(**req.model_dump()))
