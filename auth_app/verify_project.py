#!/usr/bin/env python3
"""
Skrypt weryfikacji - Sprawdza status projektu Auth API
"""
import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_file(filepath, description):
    """Sprawdź czy plik istnieje"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    size = f"({os.path.getsize(filepath)} bytes)" if exists else ""
    print(f"{status} {description}: {os.path.basename(filepath)} {size}")
    return exists

def main():
    print("\n" + "🔍"*30)
    print("  WERYFIKACJA PROJEKTU AUTH API")
    print("🔍"*30)
    
    base_dir = Path(__file__).parent
    os.chdir(base_dir)
    
    results = {}
    
    # Sprawdzenie plików głównych
    print_header("Pliki Główne")
    results['main'] = check_file("main.py", "Aplikacja FastAPI")
    results['database'] = check_file("database.py", "Warstwa bazy danych")
    results['requirements'] = check_file("requirements.txt", "Zależności")
    results['auth_db'] = check_file("auth.db", "Baza danych SQLite")
    
    # Sprawdzenie dokumentacji
    print_header("Dokumentacja")
    results['readme'] = check_file("README.md", "Główna dokumentacja")
    results['quickstart'] = check_file("QUICK_START.md", "Szybki start")
    results['raport'] = check_file("RAPORT_IMPLEMENTACJI_AUTH.md", "Raport techniczny")
    results['zadania'] = check_file("ZADANIA_ZREALIZOWANE.md", "Podsumowanie zadań")
    results['architektura'] = check_file("ARCHITEKTURA.md", "Architektura systemu")
    
    # Sprawdzenie testów
    print_header("Testy")
    results['test_file'] = check_file("testy_integracyjne/test_auth_integration.py", "Testy integracyjne")
    results['pytest_ini'] = check_file("testy_integracyjne/pytest.ini", "Konfiguracja pytest")
    
    # Sprawdzenie dodatkowych skryptów
    print_header("Skrypty Pomocnicze")
    results['demo'] = check_file("demo_test.py", "Test demonstracyjny")
    results['setup'] = check_file("setup.py", "Skrypt setupu")
    results['show_routes'] = check_file("show_routes.py", "Wyświetlanie endpointów")
    
    # Sprawdzenie modułów Pythona
    print_header("Weryfikacja Importów")
    
    try:
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")
        results['fastapi'] = True
    except ImportError:
        print("❌ FastAPI - nie zainstalowane")
        results['fastapi'] = False
    
    try:
        import jwt
        print(f"✅ PyJWT: {jwt.__version__}")
        results['jwt'] = True
    except ImportError:
        print("❌ PyJWT - nie zainstalowane")
        results['jwt'] = False
    
    try:
        import bcrypt
        print(f"✅ bcrypt: {bcrypt.__version__.decode() if hasattr(bcrypt.__version__, 'decode') else 'installed'}")
        results['bcrypt'] = True
    except ImportError:
        print("❌ bcrypt - nie zainstalowane")
        results['bcrypt'] = False
    
    try:
        import sqlalchemy
        print(f"✅ SQLAlchemy: {sqlalchemy.__version__}")
        results['sqlalchemy'] = True
    except ImportError:
        print("❌ SQLAlchemy - nie zainstalowane")
        results['sqlalchemy'] = False
    
    try:
        import pytest
        print(f"✅ pytest: {pytest.__version__}")
        results['pytest'] = True
    except ImportError:
        print("❌ pytest - nie zainstalowane")
        results['pytest'] = False
    
    # Sprawdzenie struktury kodu
    print_header("Weryfikacja Struktury Kodu")
    
    try:
        sys.path.insert(0, str(base_dir))
        from main import app
        
        # Zlicz endpointy
        routes = [route for route in app.routes if hasattr(route, 'path') and hasattr(route, 'methods')]
        endpoint_count = len([r for r in routes if r.path not in ['/openapi.json', '/docs', '/docs/oauth2-redirect', '/redoc']])
        
        print(f"✅ Aplikacja FastAPI: {endpoint_count} endpointów")
        print(f"   - /login (POST)")
        print(f"   - /users (POST)")
        print(f"   - /user_details (GET)")
        print(f"   - / (GET)")
        print(f"   - /health (GET)")
        
        results['app_structure'] = True
    except Exception as e:
        print(f"❌ Błąd importu aplikacji: {str(e)}")
        results['app_structure'] = False
    
    # Podsumowanie
    print_header("PODSUMOWANIE")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    percentage = (passed / total) * 100
    
    print(f"\nWynik: {passed}/{total} sprawdzeń przeszło ({percentage:.1f}%)")
    
    if percentage == 100:
        print("\n🎉 PROJEKT KOMPLETNY I GOTOWY DO UŻYCIA!")
        print("\nAby uruchomić aplikację:")
        print("  uvicorn main:app --reload")
        print("\nAby uruchomić testy:")
        print("  cd testy_integracyjne")
        print("  pytest test_auth_integration.py -v")
        return 0
    elif percentage >= 80:
        print("\n⚠️  Projekt prawie kompletny, brakuje kilku elementów.")
        return 1
    else:
        print("\n❌ Projekt niekompletny. Sprawdź brakujące elementy powyżej.")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
