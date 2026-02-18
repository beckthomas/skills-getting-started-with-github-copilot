import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    """Test that root endpoint redirects to static index.html"""
    response = client.get("/")
    assert response.status_code == 200
    # FastAPI's RedirectResponse returns the redirect status
    # But TestClient follows redirects by default, so we get the final response
    assert "Mergington High School" in response.text


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]


def test_signup_success():
    """Test successful signup for an activity"""
    # First, get current participants count
    response = client.get("/activities")
    initial_data = response.json()
    initial_count = len(initial_data["Tennis Club"]["participants"])

    # Sign up a new participant
    response = client.post("/activities/Tennis%20Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up test@example.com for Tennis Club" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    updated_data = response.json()
    assert len(updated_data["Tennis Club"]["participants"]) == initial_count + 1
    assert "test@example.com" in updated_data["Tennis Club"]["participants"]


def test_signup_already_signed_up():
    """Test signing up when already signed up"""
    # First sign up
    client.post("/activities/Basketball%20Team/signup?email=duplicate@example.com")

    # Try to sign up again
    response = client.post("/activities/Basketball%20Team/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up" in data["detail"]


def test_signup_activity_not_found():
    """Test signing up for non-existent activity"""
    response = client.post("/activities/NonExistent%20Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_success():
    """Test successful unregister from an activity"""
    # First sign up
    client.post("/activities/Art%20Studio/signup?email=unregister@example.com")

    # Get initial count
    response = client.get("/activities")
    initial_data = response.json()
    initial_count = len(initial_data["Art Studio"]["participants"])

    # Unregister
    response = client.delete("/activities/Art%20Studio/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered unregister@example.com from Art Studio" in data["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    updated_data = response.json()
    assert len(updated_data["Art Studio"]["participants"]) == initial_count - 1
    assert "unregister@example.com" not in updated_data["Art Studio"]["participants"]


def test_unregister_not_signed_up():
    """Test unregistering when not signed up"""
    response = client.delete("/activities/Chess%20Club/unregister?email=notsignedup@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student is not signed up" in data["detail"]


def test_unregister_activity_not_found():
    """Test unregistering from non-existent activity"""
    response = client.delete("/activities/NonExistent%20Activity/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]