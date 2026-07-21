from pydantic import BaseModel
from typing import List, Optional

class ScamCheckRequest(BaseModel):
    transcript: str
    caller_claimed_identity: Optional[str] = None
    session_id: Optional[str] = None

class ScamCheckResponse(BaseModel):
    risk_score: float
    verdict: str
    matched_patterns: List[str]
    reasoning: str
    recommended_action: str
    escalation: Optional[dict] = None
    voice_alert: Optional[str] = None

class GraphNode(BaseModel):
    id: str
    type: str                   # "phone" | "account" | "device" | "victim"
    label: str

class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str

class CasePacketRequest(BaseModel):
    case_id: str
    victim_name: Optional[str] = None
    linked_numbers: List[str]
    linked_accounts: List[str]
    summary_notes: Optional[str] = None

class GeoComplaint(BaseModel):
    lat: float
    lon: float
    complaint_type: str
    timestamp: Optional[str] = None