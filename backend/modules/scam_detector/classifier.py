from groq import Groq
from core.config import settings
from modules.scam_detector.rag_scripts import match_patterns

client = Groq(api_key=settings.GROQ_API_KEY)

SYSTEM_PROMPT = """You are Vigil, an AI fraud detection engine specialized in identifying scam calls in India, especially 'digital arrest' scams, courier scams, OTP phishing, sextortion, fake refunds, job scams, and loan scams.

You will be given a call transcript and matched known scam patterns from a reference database. Return ONLY valid JSON, no markdown, no preamble, in this exact schema:
{
  "risk_score": <0-100 integer>,
  "verdict": "SAFE" | "SUSPICIOUS" | "HIGH_RISK_SCAM",
  "reasoning": "<2-3 sentence explanation>",
  "recommended_action": "<what the citizen should do right now>"
}

Score based on presence of: impersonation of authority (police/bank/govt), threats or urgency, isolation tactics (do not tell family, do not hang up), requests for money transfer/OTP/card details/remote access apps, refusal to let victim verify independently.

IMPORTANT: Legitimate calls (bank confirming a transaction, telemarketing, delivery confirmation, appointment reminders) should score LOW even if a matched pattern appears similar — false positives on safe calls are worse than missing borderline cases. Only escalate to HIGH_RISK_SCAM when multiple red flags stack together (authority claim + urgency + money/OTP request + isolation).

Examples:
Transcript: "Hi, this is Sarah from HDFC bank confirming you made a purchase of 2000 rupees at Amazon today. Was this you?"
Output: {"risk_score": 5, "verdict": "SAFE", "reasoning": "Routine transaction confirmation with no request for sensitive info, no urgency or threats.", "recommended_action": "No action needed, this is a standard bank verification call."}

Transcript: "This is Inspector Sharma from CBI. Your Aadhaar is linked to a money laundering case. Stay on this video call, do not tell anyone, and transfer 50000 rupees to this verification account or you will be arrested within the hour."
Output: {"risk_score": 96, "verdict": "HIGH_RISK_SCAM", "reasoning": "Classic digital arrest pattern: impersonation of law enforcement, isolation instruction, extreme urgency, and demand for money transfer under threat of arrest.", "recommended_action": "Hang up immediately, do not transfer any money, verify independently by calling the police station directly, and report to cybercrime.gov.in."}

Transcript: "Sir your parcel is stuck at customs, please pay 500 rupees clearance fee or it will be destroyed, I am connecting you to customs officer now."
Output: {"risk_score": 78, "verdict": "HIGH_RISK_SCAM", "reasoning": "Courier scam pattern combining fake authority handoff and urgent payment demand for a package the victim likely never ordered.", "recommended_action": "Do not pay, hang up, and verify directly with the courier company using their official number."}
"""

def analyze_transcript(transcript: str, session_id: str = None):
    matched = match_patterns(transcript)

    user_prompt = f"""Transcript: {transcript}

Matched known scam patterns: {matched if matched else "None found"}

Analyze and return the JSON verdict."""

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=400
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    import json
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {
            "risk_score": 50,
            "verdict": "SUSPICIOUS",
            "reasoning": "Model output could not be parsed, defaulting to manual review.",
            "recommended_action": "Escalate for human review."
        }

    parsed["matched_patterns"] = matched

    from modules.scam_detector.session_tracker import record_and_check_escalation
    escalation = record_and_check_escalation(session_id, parsed["risk_score"])
    parsed["escalation"] = escalation

    if parsed["verdict"] == "HIGH_RISK_SCAM":
        parsed["voice_alert"] = f"Warning. This call shows strong signs of a scam. {parsed['recommended_action']}"
    elif parsed["verdict"] == "SUSPICIOUS":
        parsed["voice_alert"] = f"Caution. This call has some suspicious signs. {parsed['recommended_action']}"
    else:
        parsed["voice_alert"] = None

    return parsed