 Vigil — AI-Powered Digital Public Safety Intelligence Platform

Vigil is an AI-powered platform built for the ET AI Hackathon (Problem
Statement 6: Digital Public Safety) to help citizens and law enforcement
detect, disrupt, and respond to digital fraud — with a focus on India's
rapidly growing "digital arrest" scam epidemic.

**Live demo:** https://vigil-analytics.netlify.app/
**API docs:** https://vigil-backend-jyqo.onrender.com/docs

## The Problem

India registered 1.14 million cybercrime complaints in 2023, up 60% from
2022. "Digital arrest" scams alone defrauded citizens of over ₹1,776
crore in the first nine months of 2024 (Ministry of Home Affairs). These
are industrialized fraud operations, and the biggest gap in the current
system is a lack of *proactive* intelligence — tools that flag risk
before money changes hands, not after.

## What Vigil Does

Vigil covers three core capability areas from the problem statement:

### 1. Digital Arrest Scam Detector
Paste a call transcript, get an instant AI-generated verdict.
- Retrieval-augmented pattern matching against 19 known scam scripts
  across 8 fraud categories (digital arrest, courier scams, OTP
  phishing, sextortion, fake refunds, job scams, loan scams) plus
  labeled safe-call examples to minimize false positives
- Few-shot LLM reasoning (Groq, llama-3.1-8b-instant) for a risk score,
  plain-language explanation, and recommended action
- Session-level escalation tracking across repeated calls in the same
  session
- Voice warning read aloud via the browser's built-in text-to-speech

### 2. Fraud Network Graph Intelligence
Link related complaints (phone numbers, accounts) into a case, and Vigil
builds a network graph, detects likely fraud clusters via community
detection, and generates a downloadable, formatted PDF case intelligence
packet.

### 3. Geospatial Fraud Hotspot Map
An interactive map of fraud complaint density across major Indian
cities, built for patrol prioritization and resource deployment.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| LLM | Groq API — llama-3.1-8b-instant |
| Vector store | ChromaDB |
| Graph engine | NetworkX |
| PDF generation | ReportLab |
| Geospatial | Pandas (grid-based binning) |
| Frontend | HTML / Tailwind CSS / vanilla JS |
| Map | Leaflet.js + OpenStreetMap |
| Voice | Web Speech API (speechSynthesis) |
| Hosting | Render (backend) + Netlify (frontend) |

## Project Structure

vigil/
├── backend/
│ ├── main.py # FastAPI app entry point
│ ├── core/
│ │ └── config.py # env vars, API keys
│ ├── models/
│ │ └── schemas.py # Pydantic request/response models
│ ├── modules/
│ │ ├── scam_detector/
│ │ │ ├── classifier.py # Groq LLM scam classification
│ │ │ ├── rag_scripts.py # ChromaDB pattern matching
│ │ │ └── session_tracker.py # escalation tracking
│ │ ├── fraud_graph/
│ │ │ ├── graph_engine.py # NetworkX graph + clustering
│ │ │ ├── case_packet.py # case summary generation
│ │ │ └── pdf_generator.py # ReportLab PDF export
│ │ └── geo_intel/
│ │ └── hotspot.py # geospatial grid binning
│ ├── routers/
│ │ ├── scam.py
│ │ ├── graph.py
│ │ └── geo.py
│ ├── data/
│ │ ├── scam_scripts_seed.json # scam pattern corpus
│ │ └── sample_complaints.csv # synthetic geo dataset
│ └── requirements.txt
├── frontend/
│ ├── index.html # landing page
│ ├── scam-check.html # scam checker (core feature)
│ ├── fraud-map.html # geospatial hotspot map
│ └── case-intel.html # law enforcement case tool
└── README.md


## API Reference

| Method | Endpoint | Description |
|---|---|---|
| POST | `/scam/check` | Analyze a call transcript for scam risk |
| POST | `/graph/ingest` | Add a complaint's linked numbers/accounts to the fraud graph |
| GET | `/graph/data` | Retrieve the current fraud network graph |
| POST | `/graph/case-packet` | Generate a case intelligence summary (JSON) |
| POST | `/graph/case-packet/pdf` | Generate and download a formatted PDF case packet |
| GET | `/geo/hotspots` | Retrieve fraud complaint density by grid location |

Full interactive API documentation is available at `/docs` once the
backend is running.

### Example: `/scam/check`

Request:
```json
{
  "transcript": "Sir this is Inspector Sharma from CBI. Your Aadhaar is linked to a money laundering case. Stay on this call and transfer money immediately.",
  "session_id": "session_A"
}
```

Response:
```json
{
  "risk_score": 94,
  "verdict": "HIGH_RISK_SCAM",
  "matched_patterns": ["..."],
  "reasoning": "This call exhibits classic digital arrest scam indicators...",
  "recommended_action": "Hang up immediately, do not transfer money, verify independently...",
  "escalation": { "escalation_flag": true, "trend": "escalating", "history": [20, 94] },
  "voice_alert": "Warning. This call shows strong signs of a scam..."
}
```

## Running Locally

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo 'GROQ_API_KEY=your_key_here' > .env
uvicorn main:app --reload --port 8000
```
Visit `http://127.0.0.1:8000/docs` for the interactive API docs.

### Frontend
```bash
cd frontend
python3 -m http.server 5500
```
Visit `http://localhost:5500`

> Note: the frontend is pre-configured to call the deployed backend at
> `https://vigil-backend-jyqo.onrender.com`. To point it at your local
> backend instead, update the `BACKEND_URL` constant in each HTML file.

## Deployment

- **Backend** is deployed on [Render](https://render.com) (free tier).
  Build command: `pip install -r requirements.txt`. Start command:
  `uvicorn main:app --host 0.0.0.0 --port $PORT`. The `GROQ_API_KEY`
  environment variable must be set in the Render dashboard.
- **Frontend** is deployed on [Netlify](https://netlify.com) (free tier)
  as a static site.

> The backend free tier sleeps after 15 minutes of inactivity; the first
> request after a period of inactivity may take 30–50 seconds while the
> service wakes up.

## Design Philosophy

Vigil is built for citizens across all age groups and for law enforcement
investigators — not as a "hacker dashboard." The interface uses a calm,
official, government-portal-style light theme (blue/green palette, large
readable text, plain-language copy) to build trust rather than alarm,
while still communicating risk clearly when it matters.

## Future Scope

- Computer vision-based counterfeit currency detection
- Multi-channel citizen fraud shield via WhatsApp/IVR in 12 regional
  languages
- Migration from in-memory NetworkX to a persistent graph database
  (Neo4j) for production-scale case linking
- Real-time call audio ingestion via Whisper speech-to-text

## Team

Dhruv Kumar
Jaanya Dhingra

## License

Built for the ET AI Hackathon, Problem Statement 6 (Digital Public
Safety). 
