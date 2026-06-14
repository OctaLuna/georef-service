import logging
import re

import geopandas as gpd
from shapely.geometry import Point

from app.config import settings

logger = logging.getLogger(__name__)

# Loaded once at module import — Gunicorn preload_app=True ensures the parent
# process loads this before forking workers, so each worker shares the same
# memory via copy-on-write instead of duplicating the ~120 MB dataset.
try:
    _gdf = gpd.read_file(settings.geojson_path)
    # Fix any invalid geometries before queries
    _gdf["geometry"] = _gdf["geometry"].buffer(0)
    _gdf = _gdf[_gdf["geometry"].is_valid].reset_index(drop=True)
    logger.info(
        "GeoDataFrame loaded: %d features from %s",
        len(_gdf),
        settings.geojson_path,
    )
except Exception as exc:
    logger.error("Failed to load GeoDataFrame from %s: %s", settings.geojson_path, exc)
    raise RuntimeError(
        f"Cannot start service: GeoJSON file not found or invalid at '{settings.geojson_path}'. "
        "Run 'make data' to download it."
    ) from exc


# GADM 4.1 stores multi-word department names without spaces in NAME_1
_DEPT_NAMES: dict[str, str] = {
    "LaPaz": "La Paz",
    "SantaCruz": "Santa Cruz",
}

# Insert space before an uppercase letter that follows a lowercase/accented letter
# e.g. "AndrésIbáñez" → "Andrés Ibáñez", "GeneralJoséBallivián" → "General José Ballivián"
_SPLIT_WORDS = re.compile(r"(?<=[a-záéíóúüñ])(?=[A-ZÁÉÍÓÚÜÑ])")


def point_in_polygon(lat: float, lng: float) -> dict:
    """Return department/municipality for a WGS84 coordinate pair."""
    # GeoJSON uses (longitude, latitude) axis order
    point = Point(lng, lat)
    matches = _gdf[_gdf.geometry.contains(point)]
    if matches.empty:
        return {"found": False, "department": None, "municipality": None}
    row = matches.iloc[0]
    raw_dept = row.get("NAME_1")
    department = _DEPT_NAMES.get(raw_dept, raw_dept)
    raw_muni = row.get("NAME_2") or ""
    municipality = _SPLIT_WORDS.sub(" ", raw_muni) if raw_muni else None
    return {
        "found": True,
        "department": department,
        "municipality": municipality,
    }


def features_loaded() -> int:
    return len(_gdf)
