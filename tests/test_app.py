import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activity store between tests."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_expected_structure(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)
    assert "participants" in data["Chess Club"]


def test_signup_adds_participant_to_activity(client):
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]


def test_signup_duplicate_returns_400(client):
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert (
        client.get("/activities").json()[activity]["participants"].count(email) == 1
    )


def test_signup_full_activity_returns_400(client):
    # Arrange
    full_activity = "Tiny Club"
    activities[full_activity] = {
        "description": "A tiny activity",
        "schedule": "Anytime",
        "max_participants": 1,
        "participants": ["existing@mergington.edu"],
    }
    email = "new@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{full_activity}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"
