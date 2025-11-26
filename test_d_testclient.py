
import pytest
from fastapi.testclient import TestClient


def test_testclient_makes_real_http_requests(client):
    """Test weryfikujący że TestClient wykonuje rzeczywiste zapytania HTTP"""
    # TestClient symuluje prawdziwy serwer HTTP
    # Sprawdźmy różne metody HTTP
    
    # GET request
    response_get = client.get("/health")
    assert response_get.status_code == 200
    assert response_get.headers["content-type"] == "application/json"
    
    # POST request
    response_post = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"}
    )
    assert response_post.status_code == 200
    assert "access_token" in response_post.json()


def test_testclient_handles_headers(client):
    """Test że TestClient prawidłowo obsługuje nagłówki HTTP"""
    # Logowanie
    login_response = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    # Request z nagłówkiem Authorization
    response = client.get(
        "/user_details",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_testclient_handles_json_data(client):
    """Test że TestClient prawidłowo obsługuje dane JSON"""
    # Wysłanie danych JSON
    response = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    # Sprawdzenie że odpowiedź jest w formacie JSON
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert isinstance(data, dict)


def test_complete_http_flow_with_testclient(client):
    """Test kompletnego przepływu HTTP: logowanie → utworzenie użytkownika → sprawdzenie danych"""
    # 1. POST /login - otrzymanie tokena
    login_response = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 2. POST /users - utworzenie użytkownika z tokenem
    create_response = client.post(
        "/users",
        json={"username": "newuser", "password": "pass123", "role": "user"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 201
    
    # 3. POST /login - logowanie nowym użytkownikiem
    new_login = client.post(
        "/login",
        json={"username": "newuser", "password": "pass123"}
    )
    assert new_login.status_code == 200
    new_token = new_login.json()["access_token"]
    
    # 4. GET /user_details - sprawdzenie danych
    details = client.get(
        "/user_details",
        headers={"Authorization": f"Bearer {new_token}"}
    )
    assert details.status_code == 200
    assert details.json()["username"] == "newuser"


def test_testclient_respects_http_status_codes(client):
    """Test że TestClient zwraca prawidłowe kody HTTP"""
    # 200 OK
    response_200 = client.get("/health")
    assert response_200.status_code == 200
    
    # 201 Created
    login = client.post("/login", json={"username": "admin", "password": "admin123"})
    token = login.json()["access_token"]
    response_201 = client.post(
        "/users",
        json={"username": "user1", "password": "pass"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response_201.status_code == 201
    
    # 401 Unauthorized
    response_401 = client.get("/user_details")
    assert response_401.status_code == 401
    
    # 403 Forbidden (zwykły user próbuje tworzyć użytkownika)
    client.post(
        "/users",
        json={"username": "user2", "password": "pass"},
        headers={"Authorization": f"Bearer {token}"}
    )
    user_login = client.post("/login", json={"username": "user2", "password": "pass"})
    user_token = user_login.json()["access_token"]
    response_403 = client.post(
        "/users",
        json={"username": "user3", "password": "pass"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response_403.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
