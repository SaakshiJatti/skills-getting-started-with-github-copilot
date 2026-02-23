"""
Tests for the DELETE /activities/{activity_name}/unregister endpoint.
Uses AAA (Arrange-Act-Assert) pattern for test structure.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Arrange: Create a test client for the FastAPI app."""
    return TestClient(app)


class TestUnregisterFromActivity:
    """Test suite for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success_for_registered_student(self, client):
        """
        Test successful unregistration of a registered student.

        AAA Pattern:
        - Arrange: Select activity with existing participants
        - Act: Make DELETE request to unregister endpoint
        - Assert: Verify response indicates success
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Known existing participant

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity_name in result["message"]

    def test_unregister_fails_for_nonexistent_activity(self, client):
        """
        Test that unregister fails when activity does not exist.

        AAA Pattern:
        - Arrange: Prepare invalid activity name
        - Act: Make DELETE request with nonexistent activity
        - Assert: Verify error response
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()

    def test_unregister_fails_for_unregistered_student(self, client):
        """
        Test that unregister fails when student is not registered.

        AAA Pattern:
        - Arrange: Select activity and email of non-registered student
        - Act: Try to unregister the non-registered student
        - Assert: Verify error response
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "not registered" in result["detail"].lower()

    def test_unregister_requires_email_parameter(self, client):
        """
        Test that unregister endpoint requires email parameter.

        AAA Pattern:
        - Arrange: Prepare activity name without email parameter
        - Act: Make DELETE request without email parameter
        - Assert: Verify error response
        """
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister"
        )

        # Assert
        assert response.status_code == 422  # Unprocessable Entity

    def test_unregister_removes_from_participant_list(self, client):
        """
        Test that unregister removes student from activity's participant list.

        AAA Pattern:
        - Arrange: Get initial participant count
        - Act: Unregister student and fetch updated activities
        - Assert: Verify participant list is updated and count decreased
        """
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Known existing participant

        # Get initial participants
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)
        assert email in initial_participants

        # Act
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        updated_count = len(updated_participants)

        # Assert
        assert unregister_response.status_code == 200
        assert updated_count == initial_count - 1
        assert email not in updated_participants

    def test_unregister_then_signup_again(self, client):
        """
        Test that a student can sign up again after unregistering.

        AAA Pattern:
        - Arrange: Get a registered student
        - Act: Unregister and then sign up again
        - Assert: Verify student is back in participant list
        """
        # Arrange
        activity_name = "Science Club"
        email = "charlotte@mergington.edu"

        # Act
        # First, unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Then, sign up again
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Get updated activities
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]

        # Assert
        assert unregister_response.status_code == 200
        assert signup_response.status_code == 200
        assert email in final_participants
