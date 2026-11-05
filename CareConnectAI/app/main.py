"""
CareConnect AI - FastAPI Application Server
Provides REST API endpoints for Healthcare Navigation, Medical Report Simplification,
Appointment Preparation Checklists, and Emergency Protocols.
"""

import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.agent.orchestrator import CareConnectOrchestrator
from app.agent.guardrails import GuardrailManager

app = FastAPI(
    title="CareConnect AI",
    description="Intelligent Healthcare Navigation & Patient Assistance Agent",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files setup
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Initialize Master Orchestrator
orchestrator = CareConnectOrchestrator()


# Pydantic Request Models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: Optional[List[Dict[str, str]]] = None
    country: Optional[str] = "US"


class ReportDecodeRequest(BaseModel):
    text: str = Field(..., min_length=1)


class ChecklistRequest(BaseModel):
    chief_complaint: str
    duration: Optional[str] = ""
    severity: Optional[int] = 5
    medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    custom_concerns: Optional[str] = ""


class TriageRequest(BaseModel):
    symptom: str


class ApiKeyRequest(BaseModel):
    api_key: str


# Root route - serve index.html
@app.get("/")
async def root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "CareConnect AI Backend is running. Frontend static file loading..."}


# Chat / Conversation with Guardrails
@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    result = orchestrator.process_message(
        message=req.message,
        conversation_history=req.history,
        country_code=req.country or "US"
    )
    return JSONResponse(content=result)


# Medical Report Decoder (Text Input)
@app.post("/api/report/decode")
async def decode_report_text(req: ReportDecodeRequest):
    # Enforce input guardrail
    is_safe, redirect_msg, _ = GuardrailManager.inspect_user_input(req.text)
    if not is_safe:
        return JSONResponse(content={
            "detected_count": 0,
            "biomarkers": [],
            "summary": GuardrailManager.sanitize_output(redirect_msg),
            "questions_for_doctor": []
        })

    result = orchestrator.report_decoder.parse_report_text(req.text)
    result["summary"] = GuardrailManager.sanitize_output(result["summary"])
    return JSONResponse(content=result)


# Medical Report Decoder (File Upload: image or txt)
@app.post("/api/report/upload")
async def decode_report_file(file: UploadFile = File(...)):
    contents = await file.read()
    filename = file.filename or ""

    if filename.endswith(".txt") or file.content_type.startswith("text/"):
        text = contents.decode("utf-8", errors="ignore")
        result = orchestrator.report_decoder.parse_report_text(text)
        result["summary"] = GuardrailManager.sanitize_output(result["summary"])
        return JSONResponse(content=result)

    # For image uploads (JPEG/PNG), if Gemini API key is configured, use Gemini Vision
    if file.content_type.startswith("image/"):
        if orchestrator.gemini_client.is_configured():
            vision_summary = orchestrator.gemini_client.analyze_lab_report_vision(
                image_bytes=contents,
                mime_type=file.content_type
            )
            if vision_summary:
                return JSONResponse(content={
                    "detected_count": 1,
                    "biomarkers": [],
                    "summary": GuardrailManager.sanitize_output(vision_summary),
                    "questions_for_doctor": [
                        "Can you review the flagged values from this uploaded document?",
                        "What follow-up blood work is recommended?"
                    ]
                })

        # If no vision API key configured, extract any text patterns or return guide
        return JSONResponse(content={
            "detected_count": 0,
            "biomarkers": [],
            "summary": GuardrailManager.sanitize_output(
                "Image received. To enable direct image vision parsing, please configure your **Google Gemini API Key** in Settings. "
                "Alternatively, you can copy-paste the printed values (e.g. `WBC 12.4`, `Hemoglobin 11.2`) into the text box for instant offline analysis."
            ),
            "questions_for_doctor": []
        })

    return HTTPException(status_code=400, detail="Unsupported file format. Please upload .txt or image files.")


# Nearby Hospitals, Clinics & Pharmacies
@app.get("/api/clinics")
async def get_nearby_clinics(
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    facility_type: Optional[str] = Query("all"),
    radius_km: Optional[float] = Query(15.0)
):
    results = orchestrator.clinic_finder.search_nearby(
        lat=lat,
        lon=lon,
        facility_type=facility_type or "all",
        radius_km=radius_km or 15.0
    )
    return JSONResponse(content=results)


# Appointment Preparation Checklist Generator
@app.post("/api/checklist/generate")
async def generate_checklist(req: ChecklistRequest):
    result = orchestrator.checklist_agent.generate_checklist(
        chief_complaint=req.chief_complaint,
        duration=req.duration or "",
        severity=req.severity or 5,
        medications=req.medications or [],
        allergies=req.allergies or [],
        custom_concerns=req.custom_concerns or ""
    )
    result["formatted_markdown"] = GuardrailManager.sanitize_output(result["formatted_markdown"])
    return JSONResponse(content=result)


# Service Locator & Triage Guidance
@app.post("/api/triage")
async def triage_symptom(req: TriageRequest):
    result = orchestrator.service_locator.triage_symptom(req.symptom)
    return JSONResponse(content=result)


# Emergency Hotlines & Dispatch Guidance
@app.get("/api/emergency/hotlines")
async def get_emergency_hotlines():
    data = orchestrator.emergency_agent.get_all_country_hotlines()
    instructions = orchestrator.emergency_agent.dispatcher_instructions
    return JSONResponse(content={
        "countries": data,
        "dispatcher_instructions": instructions
    })


# Dynamic Gemini API Key Configuration
@app.post("/api/config/api-key")
async def configure_api_key(req: ApiKeyRequest):
    orchestrator.set_api_key(req.api_key)
    is_active = orchestrator.gemini_client.is_configured()
    return JSONResponse(content={
        "status": "success",
        "gemini_active": is_active,
        "message": "Google Gemini API key configured successfully." if is_active else "Invalid key or connection failed."
    })


# Health & Engine Status
@app.get("/api/status")
async def get_status():
    return JSONResponse(content={
        "status": "online",
        "version": "1.0.0",
        "gemini_connected": orchestrator.gemini_client.is_configured(),
        "guardrails_active": True,
        "offline_intelligence_ready": True
    })
