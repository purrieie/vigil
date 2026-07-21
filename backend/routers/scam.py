from fastapi import APIRouter
from models.schemas import ScamCheckRequest, ScamCheckResponse
from modules.scam_detector.classifier import analyze_transcript

router = APIRouter(prefix="/scam", tags=["scam-detector"])

@router.post("/check", response_model=ScamCheckResponse)
def check_scam(payload: ScamCheckRequest):
    result = analyze_transcript(payload.transcript, payload.session_id)
    return ScamCheckResponse(**result)