import logging
import time

from fastapi import APIRouter, Request

from app.config import settings
from app.models.schemas import HealthResponse, PipRequest, PipResponse
from app.services import geo_service

router = APIRouter(prefix="/geo", tags=["geo"])

logger = logging.getLogger("georef.pip")


@router.post("/pip", response_model=PipResponse, summary="Point-in-Polygon lookup")
def pip(body: PipRequest, request: Request) -> PipResponse:
    """Resolve a WGS84 coordinate pair to a Bolivian department and municipality."""
    t0 = time.perf_counter()
    result = geo_service.point_in_polygon(body.lat, body.lng)
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

    logger.info(
        "pip lat=%.4f lng=%.4f found=%s department=%s elapsed_ms=%.2f",
        body.lat,
        body.lng,
        result.get("found"),
        result.get("department"),
        elapsed_ms,
    )

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
