from fastapi import APIRouter

from app.config import settings
from app.models.schemas import HealthResponse, PipRequest, PipResponse
from app.services import geo_service

router = APIRouter(prefix="/geo", tags=["geo"])


@router.post("/pip", response_model=PipResponse, summary="Point-in-Polygon lookup")
def pip(body: PipRequest) -> PipResponse:
    """Resolve a WGS84 coordinate pair to a Bolivian department and municipality."""
    result = geo_service.point_in_polygon(body.lat, body.lng)
    return PipResponse(lat=body.lat, lng=body.lng, **result)


@router.get("/health", response_model=HealthResponse, summary="Service health")
def health() -> HealthResponse:
    """Return service status and number of loaded GeoJSON features."""
    return HealthResponse(
        status="ok",
        environment=settings.environment,
        features_loaded=geo_service.features_loaded(),
        geojson_path=settings.geojson_path,
    )
