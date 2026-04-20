from fastapi.testclient import TestClient
from main import app, ZONES

client = TestClient(app)

def test_get_crowd_density():
    """Test that crowd density endpoint returns valid JSON with all zones."""
    response = client.get("/api/crowd-density")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    
    # Ensure all defined zones exist in the output
    for zone in ZONES:
        assert zone in data
        assert isinstance(data[zone], int)
        assert 0 <= data[zone] <= 100

def test_get_wait_times():
    """Test that wait times are returned correctly and are integers."""
    response = client.get("/api/wait-times")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    
    for zone in ZONES:
        assert zone in data
        assert isinstance(data[zone], int)
        assert data[zone] >= 0

def test_get_best_route_success():
    """Test successful route calculation between valid nodes."""
    response = client.get("/api/best-route?start=North Entry&end=Food Court 1")
    assert response.status_code == 200
    data = response.json()
    
    assert data["start"] == "North Entry"
    assert data["end"] == "Food Court 1"
    assert "path" in data
    assert isinstance(data["path"], list)
    assert len(data["path"]) >= 2
    assert "estimated_time_minutes" in data

def test_get_best_route_invalid_start():
    """Test routing with a non-existent start node."""
    response = client.get("/api/best-route?start=Nowhere&end=Food Court 1")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid start or end zone provided."

def test_get_best_route_same_node():
    """Test routing when start and end are identical."""
    response = client.get("/api/best-route?start=North Entry&end=North Entry")
    assert response.status_code == 400
    assert "different" in response.json()["detail"]
