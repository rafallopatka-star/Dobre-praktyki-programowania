
import pytest
from fastapi.testclient import TestClient


def test_login_success_admin(client):
    """Test poprawnego logowania admina"""
    response = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data
    assert isinstance(data["expires_in"], int)


def test_login_invalid_credentials(client):
    """Test logowania z błędnymi danymi"""
    response = client.post(
        "/login",
        json={"username": "admin", "password": "wrong_password"}
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_nonexistent_user(client):
    """Test logowania nieistniejącego użytkownika"""
    response = client.post(
        "/login",
        json={"username": "nonexistent", "password": "password"}
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_returns_jwt_token(client):
    """Test że login zwraca prawidłowy JWT token"""
    response = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Sprawdź strukturę odpowiedzi
    assert "access_token" in data
    assert "token_type" in data
    assert "expires_in" in data
    
    # Sprawdź że token jest niepusty i ma odpowiedni format
    token = data["access_token"]
    assert len(token) > 0
    assert token.count('.') == 2  # JWT ma 3 części oddzielone kropkami


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
