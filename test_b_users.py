
import pytest
from fastapi.testclient import TestClient


def test_create_user_as_admin(client):
    """Test tworzenia użytkownika przez admina (z uprawnieniami)"""
    # Logowanie jako admin
    login_response = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    # Tworzenie nowego użytkownika
    response = client.post(
        "/users",
        json={"username": "newuser", "password": "newpass123", "role": "user"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["role"] == "user"


def test_create_user_without_token(client):
    """Test tworzenia użytkownika bez tokena (bez uprawnień)"""
    response = client.post(
        "/users",
        json={"username": "newuser", "password": "newpass123"}
    )
    assert response.status_code == 401
    assert "Invalid authorization header" in response.json()["detail"]


def test_create_user_with_invalid_token(client):
    """Test tworzenia użytkownika z nieprawidłowym tokenem"""
    response = client.post(
        "/users",
        json={"username": "newuser", "password": "newpass123"},
        headers={"Authorization": "Bearer invalid_token_xyz"}
    )
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]


def test_create_user_as_regular_user(client):
    """Test próby tworzenia użytkownika przez zwykłego użytkownika (bez uprawnień admin)"""
    # Tworzenie zwykłego użytkownika
    admin_login = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"}
    )
    admin_token = admin_login.json()["access_token"]
    
    client.post(
        "/users",
        json={"username": "regularuser", "password": "pass123", "role": "user"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Logowanie jako zwykły użytkownik
    user_login = client.post(
        "/login",
        json={"username": "regularuser", "password": "pass123"}
    )
    user_token = user_login.json()["access_token"]
    
    # Próba utworzenia użytkownika jako zwykły user (powinno się nie udać)
    response = client.post(
        "/users",
        json={"username": "anotheruser", "password": "pass123"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
    assert "Admin access required" in response.json()["detail"]


def test_create_duplicate_user(client):
    """Test tworzenia użytkownika z istniejącą nazwą"""
    login_response = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    # Próba utworzenia użytkownika z nazwą admin
    response = client.post(
        "/users",
        json={"username": "admin", "password": "newpass123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "Username already exists" in response.json()["detail"]


def test_create_user_default_role(client):
    """Test tworzenia użytkownika bez podania roli (domyślnie user)"""
    login_response = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    response = client.post(
        "/users",
        json={"username": "defaultroleuser", "password": "pass123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["role"] == "user"


def test_admin_can_create_admin(client):
    """Test że admin może tworzyć innych adminów"""
    login_response = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    response = client.post(
        "/users",
        json={"username": "admin2", "password": "admin456", "role": "admin"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["role"] == "admin"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
