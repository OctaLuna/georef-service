from pydantic import BaseModel, field_validator


class PipRequest(BaseModel):
    lat: float
    lng: float

    @field_validator("lat")
    @classmethod
    def validate_lat(cls, v: float) -> float:
        if not (-23.0 <= v <= -9.0):
            raise ValueError(
                f"lat={v} is outside Bolivia bounding box (-23.0 to -9.0). "
                "Only Bolivian coordinates are supported."
            )
        return v

    @field_validator("lng")
    @classmethod
    def validate_lng(cls, v: float) -> float:
        if not (-70.0 <= v <= -57.0):
            raise ValueError(
                f"lng={v} is outside Bolivia bounding box (-70.0 to -57.0). "
                "Only Bolivian coordinates are supported."
            )
        return v


class PipResponse(BaseModel):
    found: bool
    lat: float
    lng: float
    department: str | None
    municipality: str | None
    country: str = "Bolivia"


class HealthResponse(BaseModel):
    status: str
    environment: str
    features_loaded: int
    geojson_path: str
