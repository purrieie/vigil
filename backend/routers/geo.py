from fastapi import APIRouter
from modules.geo_intel.hotspot import compute_hotspots

router = APIRouter(prefix="/geo", tags=["geo-intel"])

@router.get("/hotspots")
def hotspots():
    return compute_hotspots()