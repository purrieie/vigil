from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import scam, graph, geo
from modules.scam_detector.rag_scripts import seed_scripts

app = FastAPI(title="Vigil - Digital Public Safety Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scam.router)
app.include_router(graph.router)
app.include_router(geo.router)

@app.on_event("startup")
def startup():
    seed_scripts()

@app.get("/")
def root():
    return {"status": "Vigil backend running"}