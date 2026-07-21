from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.pdfgen import canvas as pdfcanvas
from datetime import datetime
import hashlib
import os

OUTPUT_DIR = "generated_packets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

BRAND = colors.HexColor("#8B3A2A")
BRAND_LIGHT = colors.HexColor("#F4E3D7")
BRAND_BORDER = colors.HexColor("#E0CFC0")
GREY = colors.HexColor("#666666")


def _risk_color(score: float):
    if score >= 70:
        return colors.HexColor("#B3261E")
    if score >= 40:
        return colors.HexColor("#C77700")
    return colors.HexColor("#2E7D32")


def _case_reference(case_id: str) -> str:
    raw = f"{case_id}-{datetime.utcnow().date()}"
    return "VGL-" + hashlib.sha256(raw.encode()).hexdigest()[:10].upper()


def _draw_risk_gauge(canvas_obj, x, y, width, score):
    canvas_obj.setStrokeColor(BRAND_BORDER)
    canvas_obj.setFillColor(colors.HexColor("#EDEDED"))
    canvas_obj.roundRect(x, y, width, 0.5*cm, 3, stroke=1, fill=1)

    fill_width = width * (score / 100)
    canvas_obj.setFillColor(_risk_color(score))
    canvas_obj.roundRect(x, y, max(fill_width, 0.3*cm), 0.5*cm, 3, stroke=0, fill=1)

    canvas_obj.setFont("Helvetica-Bold", 9)
    canvas_obj.setFillColor(colors.black)
    canvas_obj.drawString(x + width + 0.3*cm, y + 0.05*cm, f"{int(score)}/100")


def _header_footer(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFont("Helvetica", 7.5)
    canvas_obj.setFillColor(GREY)
    canvas_obj.drawString(2*cm, 1.2*cm, "CONFIDENTIAL — FOR LAW ENFORCEMENT / AUTHORIZED INVESTIGATION USE ONLY")
    canvas_obj.drawRightString(19*cm, 1.2*cm, f"Page {doc.page}")
    canvas_obj.setStrokeColor(BRAND_BORDER)
    canvas_obj.line(2*cm, 1.5*cm, 19*cm, 1.5*cm)
    canvas_obj.restoreState()


def build_case_packet_pdf(packet: dict, risk_score: float = None, verdict: str = None) -> str:
    case_id = packet["case_id"]
    filepath = os.path.join(OUTPUT_DIR, f"case_packet_{case_id}.pdf")
    case_ref = _case_reference(case_id)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        topMargin=2*cm, bottomMargin=2.2*cm,
        leftMargin=2*cm, rightMargin=2*cm
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=19, textColor=BRAND, spaceAfter=2)
    subtitle_style = ParagraphStyle("SubtitleStyle", parent=styles["Normal"], fontSize=9.5, textColor=GREY, spaceAfter=4)
    ref_style = ParagraphStyle("RefStyle", parent=styles["Normal"], fontSize=9, textColor=BRAND, fontName="Helvetica-Bold")
    heading_style = ParagraphStyle("HeadingStyle", parent=styles["Heading2"], fontSize=13, textColor=BRAND, spaceBefore=16, spaceAfter=8)
    body_style = ParagraphStyle("BodyStyle", parent=styles["Normal"], fontSize=10, leading=15)

    story = []

    story.append(Paragraph("VIGIL — Case Intelligence Packet", title_style))
    story.append(Paragraph("Digital Public Safety Platform &middot; Fraud Network Intelligence Report", subtitle_style))
    story.append(Paragraph(f"Case Reference: {case_ref}", ref_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", color=BRAND_LIGHT, thickness=2))
    story.append(Spacer(1, 12))

    meta_table_data = [
        ["Case ID", packet["case_id"]],
        ["Generated At (UTC)", packet["generated_at"]],
        ["Victim / Complainant", packet.get("victim") or "Not disclosed"],
        ["Report Classification", "Fraud Network — Digital Arrest / Cyber Fraud"],
    ]
    meta_table = Table(meta_table_data, colWidths=[5*cm, 10.5*cm])
    meta_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), BRAND),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#EEEEEE")),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    if risk_score is not None:
        story.append(Paragraph("AI Risk Assessment", heading_style))
        badge_color = _risk_color(risk_score)
        risk_data = [[
            Paragraph(f"<b>Verdict:</b> {verdict or 'N/A'}", body_style),
            Paragraph(f"<b>Risk Score:</b> {int(risk_score)} / 100", body_style),
        ]]
        risk_table = Table(risk_data, colWidths=[8*cm, 7.5*cm])
        risk_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BRAND_LIGHT),
            ("BOX", (0, 0), (-1, -1), 0.5, badge_color),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 14))

    story.append(Paragraph("Summary", heading_style))
    story.append(Paragraph(packet.get("summary", "No summary provided."), body_style))

    story.append(Paragraph("Fraud Network Analysis", heading_style))
    network_data = [
        ["Metric", "Value"],
        ["Total Network Nodes", str(packet.get("network_nodes", 0))],
        ["Total Network Edges", str(packet.get("network_edges", 0))],
        ["Clusters Detected", str(packet.get("clusters_detected", 0))],
    ]
    network_table = Table(network_data, colWidths=[8*cm, 7.5*cm])
    network_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_LIGHT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.5, BRAND_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(network_table)
    story.append(Spacer(1, 8))

    clusters = packet.get("cluster_details", [])
    if clusters:
        story.append(Paragraph("Detected Fraud Clusters", heading_style))
        for i, cluster in enumerate(clusters, 1):
            cluster_text = ", ".join(cluster) if cluster else "Empty cluster"
            story.append(Paragraph(f"<b>Cluster {i}:</b> {cluster_text}", body_style))
            story.append(Spacer(1, 4))

    graph = packet.get("graph", {})
    nodes = graph.get("nodes", [])
    if nodes:
        story.append(Paragraph("Linked Entities", heading_style))
        node_rows = [["Entity", "Type"]]
        for n in nodes:
            node_rows.append([n.get("id", ""), n.get("type", "unknown")])
        node_table = Table(node_rows, colWidths=[9*cm, 6.5*cm])
        node_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_LIGHT),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, BRAND_BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(node_table)

    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "This document was auto-generated by the Vigil AI Fraud Intelligence Engine using graph-based "
        "network analysis and large language model reasoning over reported transaction, call, and device metadata. "
        "It is intended to assist investigative triage and is not a standalone legal conclusion.",
        ParagraphStyle("Disclaimer", parent=styles["Normal"], fontSize=8, textColor=GREY, leading=11)
    ))

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return filepath