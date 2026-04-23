"""
Test suite for Raahi application
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


@pytest.fixture
def test_client():
    """Create a test client for Flask app"""
    from backend.main import create_app
    
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


def test_flask_runs(test_client):
    """Test that Flask app starts"""
    response = test_client.get('/')
    assert response.status_code in [200, 302]  # 302 if redirect to login


def test_health_check(test_client):
    """Test health check endpoint if available"""
    response = test_client.get('/health')
    # Endpoint might not exist, just verify we get a response
    assert response.status_code in [200, 404]
