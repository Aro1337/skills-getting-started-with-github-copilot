"""
Tests for the High School Management System API

Uses AAA (Arrange-Act-Assert) pattern for clear test structure.
Each test isolates the activities data using the reset_activities fixture.
"""

import pytest
from src.app import activities


class TestGetActivities:
    """GET /activities endpoint tests"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        # Arrange
        expected_count = len(activities)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()) == expected_count
    
    def test_get_activities_returns_correct_structure(self, client, reset_activities):
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert isinstance(data, dict)
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """POST /activities/{activity_name}/signup endpoint tests"""
    
    def test_signup_successful(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1
    
    def test_signup_activity_not_found(self, client, reset_activities):
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
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_registered(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in participants
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_students_same_activity(self, client, reset_activities):
        # Arrange
        activity_name = "Programming Class"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]


class TestRemoveParticipant:
    """DELETE /activities/{activity_name}/participant/{email} endpoint tests"""
    
    def test_remove_participant_successful(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in participants
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant/{email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1
    
    def test_remove_activity_not_found(self, client, reset_activities):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_remove_participant_not_found(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_remove_multiple_participants(self, client, reset_activities):
        # Arrange
        activity_name = "Art Studio"
        email1 = "noah@mergington.edu"
        email2 = "ava@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response1 = client.delete(
            f"/activities/{activity_name}/participant/{email1}"
        )
        response2 = client.delete(
            f"/activities/{activity_name}/participant/{email2}"
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 not in activities[activity_name]["participants"]
        assert email2 not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 2


class TestIntegration:
    """Integration tests combining multiple operations"""
    
    def test_signup_and_remove_workflow(self, client, reset_activities):
        # Arrange
        activity_name = "Basketball Team"
        email = "basketball_fan@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert signup
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]
        
        # Act - Remove
        remove_response = client.delete(
            f"/activities/{activity_name}/participant/{email}"
        )
        
        # Assert remove
        assert remove_response.status_code == 200
        assert email not in activities[activity_name]["participants"]
    
    def test_cannot_remove_after_signup_duplicate_attempt(self, client, reset_activities):
        # Arrange
        activity_name = "Drama Club"
        email = "actor@mergington.edu"
        
        # Act - Sign up successfully
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Act - Try to sign up again (should fail)
        duplicate_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert duplicate_response.status_code == 400
        # Verify participant count is still 1 (not 2)
        assert activities[activity_name]["participants"].count(email) == 1
