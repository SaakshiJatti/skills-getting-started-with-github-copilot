"""
Tests for the POST /activities/{activity_name}/signup endpoint.
Uses AAA (Arrange-Act-Assert) pattern for test structure.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Arrange: Create a test client for the FastAPI app."""
    return TestClient(app)


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success_for_new_student(self, client):
        """
        Test successful signup of a new student for an activity.

        AAA Pattern:
        - Arrange: Prepare test data (activity and email)
        - Act: Make POST request to signup endpoint
        - Assert: Verify response indicates success
        """
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
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity_name in result["message"]

    def test_signup_fails_for_nonexistent_activity(self, client):
        """
        Test that signup fails when activity does not exist.

        AAA Pattern:
        - Arrange: Prepare invalid activity name and student email
        - Act: Make POST request with nonexistent activity
        - Assert: Verify error response
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()

    def test_signup_fails_for_duplicate_student(self, client):
        """
        Test that signup fails when student is already registered.

        AAA Pattern:
        - Arrange: Get an existing activity and a student already registered
        - Act: Try to signup the same student again
        - Assert: Verify error response for duplicate signup
        """
        # Arrange
        activity_name = "Chess Club"
        # Michael is already registered for Chess Club
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"].lower()

    def test_signup_requires_email_parameter(self, client):
        """
        Test that signup endpoint requires email parameter.

        AAA Pattern:
        - Arrange: Prepare activity name without email parameter
        - Act: Make POST request without email parameter
        - Assert: Verify error response
        """
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup"
        )

        # Assert
        assert response.status_code == 422  # Unprocessable Entity

    def test_signup_updates_participant_list(self, client):
        """
        Test that signup adds student to activity's participant list.

        AAA Pattern:
        - Arrange: Prepare test data and get initial participant count
        - Act: Signup new student and fetch activities
        - Assert: Verify participant list is updated
        """
        # Arrange
        activity_name = "Drama Club"
        email = "teststudent@mergington.edu"

        # Get initial participants
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)

        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        updated_count = len(updated_participants)

        # Assert
        assert signup_response.status_code == 200
        assert updated_count == initial_count + 1
        assert email in updated_participants
