"""
Tests for the GET /activities endpoint.
Uses AAA (Arrange-Act-Assert) pattern for test structure.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Arrange: Create a test client for the FastAPI app."""
    return TestClient(app)


class TestGetActivities:
    """Test suite for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Test that GET /activities returns all activities with correct structure.

        AAA Pattern:
        - Arrange: Test client is ready (via fixture)
        - Act: Make GET request to /activities
        - Assert: Verify response status and content structure
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_get_activities_returns_correct_structure(self, client):
        """
        Test that each activity has the required fields.

        AAA Pattern:
        - Arrange: Test client is ready
        - Act: Make GET request to /activities
        - Assert: Verify each activity has required fields
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_details in activities.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_contains_expected_activities(self, client):
        """
        Test that specific expected activities are present.

        AAA Pattern:
        - Arrange: Define expected activity names
        - Act: Make GET request to /activities
        - Assert: Verify all expected activities exist
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Drama Club",
            "Art Studio",
            "Debate Team",
            "Science Club"
        ]

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name in expected_activities:
            assert activity_name in activities
