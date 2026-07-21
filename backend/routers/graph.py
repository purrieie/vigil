from fastapi import APIRouter
from fastapi.responses import FileResponse
from models.schemas import CasePacketRequest
from modules.fraud_graph.graph_engine import add_case_data, get_graph_json
from modules.fraud_graph.case_packet import generate_case_packet
from modules.fraud_graph.pdf_generator import build_case_packet_pdf

router = APIRouter(prefix="/graph", tags=["fraud-graph"])

@router.post("/ingest")
def ingest_case(payload: CasePacketRequest):
    return add_case_data(
        case_id=payload.case_id,
        numbers=payload.linked_numbers,
        accounts=payload.linked_accounts,
        victim=payload.victim_name
    )

@router.get("/data")
def graph_data():
    return get_graph_json()

@router.post("/case-packet")
def case_packet(payload: CasePacketRequest):
    return generate_case_packet(payload.case_id, payload.victim_name, payload.summary_notes)

@router.post("/case-packet/pdf")
def case_packet_pdf(payload: CasePacketRequest):
    packet = generate_case_packet(payload.case_id, payload.victim_name, payload.summary_notes)
    filepath = build_case_packet_pdf(packet, risk_score=88, verdict="HIGH_RISK_SCAM")
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=f"vigil_case_packet_{payload.case_id}.pdf"
    )