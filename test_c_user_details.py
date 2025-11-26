
import pytest
from fastapi.testclient import TestClient


def test_get_user_details_with_valid_token(client):
    """Test pobierania szczegółów użytkownika z prawidłowym tokenem (poprawna autoryzacja)"""
    # Logowanie
    login_response = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    # Pobieranie szczegółów
    response = client.get(
        "/user_details",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["role"] == "admin"
    assert "iat" in data
    assert "exp" in data
    assert isinstance(data["iat"], int)
    assert isinstance(data["exp"], int)


def test_get_user_details_without_token(client):
    """Test pobierania szczegółów bez tokena (brak autoryzacji)"""
    response = client.get("/user_details")
    assert response.status_code == 401
    assert "Invalid authorization header" in response.json()["detail"]


def test_get_user_details_with_invalid_token(client):
    """Test pobierania szczegółów z nieprawidłowym tokenem"""
    response = client.get(
        "/user_details",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]


def test_get_user_details_missing_authorization_header(client):
    """Test żądania bez nagłówka Authorization"""
    response = client.get("/user_details")
    assert response.status_code == 401


def test_get_user_details_malformed_authorization_header(client):
    """Test błędnie sformatowanego nagłówka Authorization"""
    response = client.get(
        "/user_details",
        headers={"Authorization": "InvalidFormat"}
    )
    assert response.status_code == 401


def test_get_user_details_bearer_without_token(client):
    """Test nagłówka Bearer bez tokena"""
    response = client.get(
        "/user_details",
        headers={"Authorization": "Bearer "}
    )
    assert response.status_code == 401


def test_get_user_details_for_regular_user(client):
    """Test pobierania szczegółów dla zwykłego użytkownika"""
    # Admin tworzy zwykłego użytkownika
    admin_login = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"}
    )
    admin_token = admin_login.json()["access_token"]
    
    client.post(
        "/users",
        json={"username": "testuser", "password": "pass123", "role": "user"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Logowanie jako zwykły użytkownik
    user_login = client.post(
        "/login",
        json={"username": "testuser", "password": "pass123"}
    )
    user_token = user_login.json()["access_token"]
    
    # Sprawdzenie danych użytkownika
    response = client.get(
        "/user_details",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == "user"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
