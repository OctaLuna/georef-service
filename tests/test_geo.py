"""
Integration tests for the GeoRef microservice.

Requires that data/bolivia.geojson exists (run `make data` first).
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealth:
    def test_health_returns_ok(self):
        response = client.get("/geo/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["features_loaded"] > 0

    def test_health_has_required_fields(self):
        response = client.get("/geo/health")
        data = response.json()
        assert "environment" in data
        assert "features_loaded" in data
        assert "geojson_path" in data


class TestPip:
    def test_santa_cruz_de_la_sierra(self):
        """Central coordinate of Santa Cruz de la Sierra."""
        response = client.post("/geo/pip", json={"lat": -17.7833, "lng": -63.1821})
        assert response.status_code == 200
        data = response.json()
        assert data["found"] is True
        assert data["department"] == "Santa Cruz"
        assert data["municipality"] is not None
        assert data["country"] == "Bolivia"

    def test_la_paz_city(self):
        """Central coordinate of La Paz."""
        response = client.post("/geo/pip", json={"lat": -16.5000, "lng": -68.1500})
        assert response.status_code == 200
        data = response.json()
        assert data["found"] is True
        assert data["department"] == "La Paz"

    def test_cochabamba_city(self):
        """Central coordinate of Cochabamba."""
        response = client.post("/geo/pip", json={"lat": -17.3895, "lng": -66.1568})
        assert response.status_code == 200
        data = response.json()
        assert data["found"] is True
        assert data["department"] == "Cochabamba"

    def test_response_echoes_coordinates(self):
        response = client.post("/geo/pip", json={"lat": -17.7833, "lng": -63.1821})
        data = response.json()
        assert abs(data["lat"] - (-17.7833)) < 0.0001
        assert abs(data["lng"] - (-63.1821)) < 0.0001

    def test_out_of_range_lat_returns_422(self):
        """Coordinates outside Bolivia (New York) must be rejected."""
        response = client.post("/geo/pip", json={"lat": 40.7128, "lng": -74.0060})
        assert response.status_code == 422

    def test_out_of_range_lng_returns_422(self):
        """Longitude outside Bolivia range."""
        response = client.post("/geo/pip", json={"lat": -17.0, "lng": -50.0})
        assert response.status_code == 422

    def test_lat_too_far_north_returns_422(self):
        response = client.post("/geo/pip", json={"lat": -8.0, "lng": -63.0})
        assert response.status_code == 422

    def test_lat_too_far_south_returns_422(self):
        response = client.post("/geo/pip", json={"lat": -24.0, "lng": -63.0})
        assert response.status_code == 422

    def test_missing_fields_returns_422(self):
        response = client.post("/geo/pip", json={"lat": -17.7833})
        assert response.status_code == 422

    def test_non_numeric_fields_returns_422(self):
        response = client.post("/geo/pip", json={"lat": "abc", "lng": -63.0})
        assert response.status_code == 422
