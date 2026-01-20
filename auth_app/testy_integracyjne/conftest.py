"""
Wspólna konfiguracja dla wszystkich testów integracyjnych
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os

# Dodaj ścieżkę do modułu auth_app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import Base, get_db, User, hash_password

# Baza testowa w pamięci
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override dependency dla testowej bazy danych"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Przygotowanie czystej bazy przed każdym testem"""
    # Usuń starą bazę jeśli istnieje
    Base.metadata.drop_all(bind=test_engine)
    
    # Utwórz nową strukturę
    Base.metadata.create_all(bind=test_engine)
    
    # Dodaj domyślnego admina
    db = TestingSessionLocal()
    try:
        admin = User(
            username="admin",
            hashed_password=hash_password("admin123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
    finally:
        db.close()
    
    yield
    
    # Czyszczenie po teście
    Base.metadata.drop_all(bind=test_engine)


# Override dependency
app.dependency_overrides[get_db] = override_get_db

# Wyłącz startup event
app.router.on_startup = []


@pytest.fixture(scope="module")
def client():
    """Fixture zwracający TestClient"""
    return TestClient(app)
