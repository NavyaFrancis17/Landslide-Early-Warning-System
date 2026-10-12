"""
Unit tests for FastAPI backend REST API endpoints (Phase 8 Upgrade).
"""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"


def test_api_dashboard_summary():
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_observations" in data
    assert "state_distribution" in data


def test_api_locations():
    res = client.get("/api/locations?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    if data:
        assert "location_id" in data[0]
        assert "place_name" in data[0]
        assert "country" in data[0]


def test_api_locations_search():
    res = client.get("/api/locations/search?q=kerala")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)


def test_api_location_detail():
    locs_res = client.get("/api/locations?limit=1")
    locs = locs_res.json()
    if locs:
        loc_id = locs[0]["location_id"]
        res = client.get(f"/api/location/{loc_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["location_id"] == loc_id
        assert "place_name" in data
        assert "adaptive_analysis" in data


def test_api_warnings():
    res = client.get("/api/warnings?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "items" in data


def test_api_evaluation_summary():
    res = client.get("/api/evaluation/summary")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data


def test_api_simulation_scenarios():
    res = client.get("/api/simulation/scenarios")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_api_simulation_run():
    locs_res = client.get("/api/locations?limit=1")
    locs = locs_res.json()
    if locs:
        loc_id = locs[0]["location_id"]
        payload = {
            "location_id": loc_id,
            "rainfall_multiplier": 1.25,
            "soil_moisture_multiplier": 1.10,
            "scenario_name": "test_run",
        }
        res = client.post("/api/simulation/run", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "comparison" in data
        assert "place_name" in data
