import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provides a FastAPI TestClient for making HTTP requests"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Resets activities to original state before each test for test isolation"""
    # Store original state
    original_activities = copy.deepcopy(activities)
    
    # Yield to test
    yield
    
    # Restore original state after test
    activities.clear()
    activities.update(original_activities)
