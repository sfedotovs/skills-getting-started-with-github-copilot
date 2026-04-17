"""
Tests for the High School Management System API using AAA pattern.
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


# Create a deep copy at module load to use as the baseline
BASELINE_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities_state():
    """
    Fixture to reset activities state before and after each test.
    This prevents test interactions and ensures isolation.
    """
    # Arrange: Clear and restore activities to baseline state
    activities.clear()
    activities.update(copy.deepcopy(BASELINE_ACTIVITIES))
    
    yield  # Allow test to run
    
    # Assert-like cleanup: Restore state after test
    activities.clear()
    activities.update(copy.deepcopy(BASELINE_ACTIVITIES))


@pytest.fixture
def client():
    """Fixture to provide a test client for API requests."""
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities."""
        # Arrange
        expected_activities = {
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Club", "Tennis Club", "Art Club",
            "Music Ensemble", "Robotics Team", "Debate Club"
        }
        
        # Act
        response = client.get("/activities")
        returned_activities = set(response.json().keys())
        
        # Assert
        assert response.status_code == 200
        assert returned_activities == expected_activities
    
    def test_get_activities_contains_required_fields(self, client):
        """Test that each activity contains required fields."""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in activities_data.items():
            assert set(activity_data.keys()) == required_fields


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
    
    def test_signup_for_activity_returns_404_when_activity_not_found(self, client):
        """Test signup returns 404 for nonexistent activity."""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_for_activity_returns_400_when_already_registered(self, client):
        """Test signup returns 400 when student is already signed up."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"


class TestUnregisterParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""
    
    def test_unregister_participant_success(self, client):
        """Test successful unregistration from an activity."""
        # Arrange
        activity_name = "Basketball Club"
        email = "lucas@mergington.edu"  # Already registered
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_returns_404_when_activity_not_found(self, client):
        """Test unregister returns 404 for nonexistent activity."""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_returns_404_when_participant_not_found(self, client):
        """Test unregister returns 404 when participant is not registered."""
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found for this activity"
