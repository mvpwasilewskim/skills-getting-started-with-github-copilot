"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original activities
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis skills development and friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["alex@mergington.edu", "sarah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts exploration",
            "schedule": "Mondays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Orchestra and band performance group",
            "schedule": "Wednesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["lucas@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore science through experiments and projects",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["mason@mergington.edu", "chloe@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(original)
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that get_activities returns all available activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_contains_activity_details(self, client, reset_activities):
        """Test that each activity contains required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_contains_participants(self, client, reset_activities):
        """Test that activities contain participant information"""
        response = client.get("/activities")
        data = response.json()
        
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant_to_list(self, client, reset_activities):
        """Test that signup actually adds participant to the activity"""
        client.post(
            "/activities/Basketball Team/signup",
            params={"email": "newplayer@mergington.edu"}
        )
        
        response = client.get("/activities")
        activity = response.json()["Basketball Team"]
        assert "newplayer@mergington.edu" in activity["participants"]
        assert len(activity["participants"]) == 2
    
    def test_signup_duplicate_email_fails(self, client, reset_activities):
        """Test that duplicate signup returns 400 error"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test signing up multiple different students"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                "/activities/Tennis Club/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        response = client.get("/activities")
        activity = response.json()["Tennis Club"]
        assert len(activity["participants"]) == 5


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client, reset_activities):
        """Test successful unregister from an activity"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes participant from activity"""
        client.post(
            "/activities/Chess Club/unregister",
            params={"email": "daniel@mergington.edu"}
        )
        
        response = client.get("/activities")
        activity = response.json()["Chess Club"]
        assert "daniel@mergington.edu" not in activity["participants"]
        assert len(activity["participants"]) == 1
    
    def test_unregister_not_signed_up_fails(self, client, reset_activities):
        """Test that unregister for non-participant returns 400"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "notparticipant@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregister from non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_all_participants(self, client, reset_activities):
        """Test unregistering all participants from an activity"""
        participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        for email in participants:
            response = client.post(
                "/activities/Chess Club/unregister",
                params={"email": email}
            )
            assert response.status_code == 200
        
        response = client.get("/activities")
        activity = response.json()["Chess Club"]
        assert len(activity["participants"]) == 0


class TestSignupAndUnregisterFlow:
    """Tests for combined signup and unregister flows"""
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up and then unregistering"""
        email = "testuser@mergington.edu"
        activity = "Programming Class"
        
        # Sign up
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
    
    def test_signup_unregister_signup_again(self, client, reset_activities):
        """Test signing up, unregistering, and signing up again"""
        email = "testuser@mergington.edu"
        activity = "Art Studio"
        
        # First signup
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Unregister
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Sign up again (should work)
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
