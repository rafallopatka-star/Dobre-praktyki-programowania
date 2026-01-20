# 🔐 System Uwierzytelniania JWT - Auth API

Kompletny system uwierzytelniania oparty na FastAPI i JSON Web Tokens (JWT) z kontrolą dostępu opartą na rolach (RBAC).

## 📋 Spis Treści

- [Funkcjonalności](#funkcjonalności)
- [Technologie](#technologie)
- [Szybki Start](#szybki-start)
- [Endpointy API](#endpointy-api)
- [Bezpieczeństwo](#bezpieczeństwo)
- [Testy](#testy)
- [Dokumentacja](#dokumentacja)

## ✨ Funkcjonalności

### Zaimplementowane Wymagania (8/8)

- ✅ **POST /login** - Uwierzytelnianie użytkownika i generowanie JWT
- ✅ **Model User** - Tabela użytkowników w bazie SQLite
- ✅ **Weryfikacja bazy** - Sprawdzanie użytkownika w bazie podczas logowania
- ✅ **POST /users** - Dodawanie nowych użytkowników (admin only)
- ✅ **Zabezpieczenie JWT** - Wymagany nagłówek `Authorization: Bearer <token>`
- ✅ **Kontrola ról** - ROLE_ADMIN dla tworzenia użytkowników
- ✅ **GET /user_details** - Zwracanie danych użytkownika z tokena
- ✅ **Testy integracyjne** - 21 testów pokrywających wszystkie scenariusze

### Dodatkowe Funkcje

- 🔒 Hashowanie haseł (bcrypt)
- 🎫 JWT z podpisem cyfrowym i czasem wygaśnięcia
- 🛡️ Role-Based Access Control (RBAC)
- 📝 Automatyczna dokumentacja API (Swagger/ReDoc)
- 🧪 Kompleksowe testy integracyjne z pytest
- 🔄 Automatyczna inicjalizacja bazy i konta admin
- ✅ Walidacja danych wejściowych (Pydantic)

## 🛠️ Technologie

| Technologia | Wersja | Zastosowanie |
|-------------|--------|--------------|
| Python | 3.13.7 | Język programowania |
| FastAPI | 0.104.1 | Web framework |
| SQLAlchemy | 2.0.23 | ORM dla bazy danych |
| PyJWT | 2.8.1 | JSON Web Tokens |
| bcrypt | 4.1.2 | Hashowanie haseł |
| pytest | 7.4.3 | Framework testowy |
| uvicorn | 0.24.0 | ASGI server |
| Pydantic | 2.5.2 | Walidacja danych |

## 🚀 Szybki Start

### 1. Instalacja

```bash
# Przejdź do katalogu projektu
cd Pliki_zajecia/auth_app

# Zainstaluj zależności
pip install -r requirements.txt
```

### 2. Uruchomienie

```bash
# Uruchom serwer deweloperski
uvicorn main:app --reload
```

Serwer będzie dostępny pod adresem: **http://localhost:8000**

### 3. Dokumentacja API

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 4. Domyślne Konto

System automatycznie tworzy konto administratora:

```
Username: admin
Password: admin123
```

⚠️ **W produkcji natychmiast zmień to hasło!**

## 📡 Endpointy API

### Publiczne (bez autoryzacji)

| Metoda | Endpoint | Opis |
|--------|----------|------|
| GET | `/` | Strona główna z informacjami |
| GET | `/health` | Health check |
| POST | `/login` | Logowanie i otrzymanie tokena JWT |

### Chronione (wymagany token)

| Metoda | Endpoint | Opis | Rola |
|--------|----------|------|------|
| GET | `/user_details` | Dane zalogowanego użytkownika | Any |
| POST | `/users` | Tworzenie nowego użytkownika | Admin |

## 🔐 Bezpieczeństwo

### Implementowane Mechanizmy

1. **Hashowanie Haseł**
   - Algorytm: bcrypt z automatycznym salt
   - Hasła nigdy nie są przechowywane w plain text

2. **JWT Tokens**
   - Algorytm: HS256
   - Czas wygaśnięcia: 1 godzina
   - Payload: username, role, iat, exp

3. **Kontrola Dostępu**
   - Role-Based Access Control (RBAC)
   - Weryfikacja tokena przy każdym request
   - Separacja uprawnień admin/user

4. **Walidacja**
   - Pydantic models dla request/response
   - Właściwe kody HTTP status
   - Bezpieczne komunikaty błędów

### Format Tokena

```json
{
  "sub": "username",
  "role": "admin",
  "iat": 1699800000,
  "exp": 1699803600
}
```

### Przykład Użycia

```bash
# 1. Logowanie
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Odpowiedź:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIs...",
#   "token_type": "bearer",
#   "expires_in": 3600
# }

# 2. Użycie tokena
curl http://localhost:8000/user_details \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

## 🧪 Testy

### Uruchomienie Testów

```bash
# Wszystkie testy
cd testy_integracyjne
pytest test_auth_integration.py -v

# Konkretna klasa testów
pytest test_auth_integration.py::TestAuthentication -v

# Z pokryciem kodu
pytest test_auth_integration.py --cov=../ --cov-report=html
```

### Statystyki Testów

- **Całkowita liczba testów:** 21
- **Status:** ✅ Wszystkie przechodzą
- **Czas wykonania:** ~7.65s
- **Pokrycie:** 100% endpointów

### Grupy Testów

| Grupa | Liczba | Opis |
|-------|--------|------|
| TestHealthAndRoot | 2 | Podstawowe endpointy |
| TestAuthentication | 3 | Logowanie (poprawne/błędne) |
| TestUserCreation | 6 | Tworzenie użytkowników |
| TestUserDetails | 3 | Pobieranie danych użytkownika |
| TestCompleteUserFlow | 2 | Kompletne scenariusze |
| TestTokenSecurity | 3 | Bezpieczeństwo tokenów |
| TestRoleBasedAccess | 2 | Kontrola dostępu |

### Demo Test

Uruchom interaktywny test demonstracyjny:

```bash
# Najpierw uruchom serwer
uvicorn main:app --reload

# W drugim terminalu
python demo_test.py
```

## 📚 Dokumentacja

| Plik | Opis |
|------|------|
| `QUICK_START.md` | Szybki przewodnik użytkownika |
| `RAPORT_IMPLEMENTACJI_AUTH.md` | Pełny raport techniczny |
| `testy_integracyjne/README.md` | Dokumentacja testów |
| `testy_integracyjne/RAPORT_IMPLEMENTACJI.md` | Raport testów |

## 📁 Struktura Projektu

```
auth_app/
├── main.py                      # Główna aplikacja FastAPI
├── database.py                  # Modele i operacje DB
├── requirements.txt             # Zależności
├── auth.db                      # Baza danych SQLite
├── QUICK_START.md              # Szybki start
├── RAPORT_IMPLEMENTACJI_AUTH.md # Pełna dokumentacja
├── demo_test.py                # Test demonstracyjny
├── setup.py                    # Skrypt setupu
├── show_routes.py              # Wyświetlanie endpointów
└── testy_integracyjne/
    ├── test_auth_integration.py # Testy integracyjne
    ├── pytest.ini               # Konfiguracja pytest
    ├── README.md                # Dokumentacja testów
    └── RAPORT_IMPLEMENTACJI.md  # Raport testów
```

## 🔧 Konfiguracja

### Zmienne Konfiguracyjne (main.py)

```python
SECRET_KEY = "super_secret_key_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 1
```

### Baza Danych (database.py)

```python
DATABASE_URL = "sqlite:///./auth.db"
```

## 🎯 Use Cases

### 1. Administrator tworzy użytkownika

```bash
# Login jako admin
TOKEN=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# Tworzenie użytkownika
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"username":"developer","password":"dev123","role":"user"}'
```

### 2. Użytkownik sprawdza swoje dane

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"developer","password":"dev123"}' | jq -r '.access_token')

# Pobieranie danych
curl http://localhost:8000/user_details \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Próba nieuprawnionego dostępu

```bash
# Zwykły user próbuje utworzyć użytkownika
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{"username":"hacker","password":"hack123"}'

# Odpowiedź: 403 Forbidden - Admin access required
```

## 🐛 Rozwiązywanie Problemów

### Serwer nie startuje
```bash
# Sprawdź czy port 8000 jest wolny
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Uruchom na innym porcie
uvicorn main:app --reload --port 8001
```

### Błąd "Invalid credentials"
- Sprawdź username i password
- Domyślne konto: admin/admin123
- Sprawdź czy baza danych została zainicjalizowana

### Błąd "Invalid token"
- Sprawdź format: `Authorization: Bearer <token>`
- Token wygasa po 1 godzinie
- Zaloguj się ponownie

### Wszystkie testy failują
```bash
# Sprawdź czy dependencies są zainstalowane
pip install -r requirements.txt

# Sprawdź wersję Pythona
python --version  # Powinno być 3.7+

# Uruchom testy z verbose
pytest -vv
```

## 📊 Metryki

- **Linie kodu:** ~500 (main + database + tests)
- **Pokrycie testami:** 100% endpointów
- **Czas startu:** ~1s
- **Czas odpowiedzi:** <50ms
- **Testy:** 21/21 ✅

## 🔄 Roadmap

### Możliwe Rozszerzenia

- [ ] Refresh tokens
- [ ] Rate limiting
- [ ] Email verification
- [ ] Password reset
- [ ] OAuth2 providers (Google, GitHub)
- [ ] Redis dla sesji
- [ ] Audit log
- [ ] Two-factor authentication (2FA)
- [ ] Token blacklist
- [ ] Password complexity requirements

## 👥 Autorzy

System stworzony jako część kursu "Dobre Praktyki Programowania"

## 📄 Licencja

Projekt edukacyjny - do użytku dydaktycznego

---

## 🎓 Nauka

Ten projekt demonstruje:
- ✅ RESTful API design
- ✅ JWT authentication
- ✅ Role-based access control
- ✅ Database integration (SQLAlchemy)
- ✅ Password hashing (bcrypt)
- ✅ Integration testing (pytest)
- ✅ API documentation (OpenAPI)
- ✅ Dependency injection (FastAPI)
- ✅ Error handling
- ✅ Security best practices

---

**System gotowy do użycia! 🚀**

Więcej informacji w:
- `QUICK_START.md` - Szybki start
- `RAPORT_IMPLEMENTACJI_AUTH.md` - Pełna dokumentacja techniczna
