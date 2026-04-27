import pytest
from httpx import AsyncClient
from fastapi import status
from src.app import app, activities

import copy

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: Save original state and restore after test
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))

@pytest.mark.asyncio
async def test_get_activities():
    # Arrange
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Act
        response = await ac.get("/activities")
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()

@pytest.mark.asyncio
async def test_signup_for_activity():
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Act
        response = await ac.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert email in activities[activity]["participants"]

@pytest.mark.asyncio
async def test_signup_duplicate():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Act
        response = await ac.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already signed up" in response.json()["detail"]

@pytest.mark.asyncio
async def test_unregister_participant():
    # Arrange
    email = "daniel@mergington.edu"
    activity = "Chess Club"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Act
        response = await ac.delete(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert email not in activities[activity]["participants"]

@pytest.mark.asyncio
async def test_unregister_nonexistent_participant():
    # Arrange
    email = "ghost@mergington.edu"
    activity = "Chess Club"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Act
        response = await ac.delete(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not registered" in response.json()["detail"]
