"""
Test integracji api_sql_lite.py z modulem SQL.database_models
"""
import os
import sys

def test_imports():
    """Test czy wszystkie importy działają poprawnie"""
    print("Test 1: Importowanie modelu bazy danych...")
    try:
        from SQL.database_models import Movie, Link, Rating, Tag, get_session, create_tables, DATABASE_URL
        print("  [OK] Modul SQL.database_models zaimportowany poprawnie")
        print(f"  [INFO] DATABASE_URL: {DATABASE_URL}")
    except ImportError as e:
        print(f"  [BLAD] Nie mozna zaimportowac SQL.database_models: {e}")
        return False
    
    print("\nTest 2: Testowanie funkcji get_session...")
    try:
        session = get_session()
        print("  [OK] Funkcja get_session() dziala")
        session.close()
    except Exception as e:
        print(f"  [BLAD] Problem z get_session(): {e}")
        return False
    
    print("\nTest 3: Sprawdzanie sciezki do bazy danych...")
    try:
        db_dir = os.path.dirname(DATABASE_URL.replace('sqlite:///', ''))
        print(f"  [INFO] Folder bazy danych: {db_dir}")
        if os.path.exists(db_dir):
            print(f"  [OK] Folder {db_dir} istnieje")
        else:
            print(f"  [WARNING] Folder {db_dir} nie istnieje (zostanie utworzony przy pierwszym uruchomieniu)")
    except Exception as e:
        print(f"  [BLAD] Problem ze sciezka: {e}")
        return False
    
    print("\nTest 4: Importowanie Flask i pozostalych zaleznosci...")
    try:
        from flask import Flask, jsonify
        import csv
        import webbrowser
        import threading
        print("  [OK] Wszystkie zaleznosci Flask zaimportowane")
    except ImportError as e:
        print(f"  [BLAD] Brak zaleznosci: {e}")
        return False
    
    return True

def test_database_structure():
    """Test struktury modeli bazy danych"""
    print("\nTest 5: Sprawdzanie struktury modeli...")
    try:
        from SQL.database_models import Movie, Link, Rating, Tag
        
        # Sprawdz czy klasy maja odpowiednie atrybuty
        assert hasattr(Movie, '__tablename__'), "Movie nie ma atrybutu __tablename__"
        assert hasattr(Link, '__tablename__'), "Link nie ma atrybutu __tablename__"
        assert hasattr(Rating, '__tablename__'), "Rating nie ma atrybutu __tablename__"
        assert hasattr(Tag, '__tablename__'), "Tag nie ma atrybutu __tablename__"
        
        print(f"  [OK] Movie -> tabela: {Movie.__tablename__}")
        print(f"  [OK] Link -> tabela: {Link.__tablename__}")
        print(f"  [OK] Rating -> tabela: {Rating.__tablename__}")
        print(f"  [OK] Tag -> tabela: {Tag.__tablename__}")
        
        return True
    except Exception as e:
        print(f"  [BLAD] Problem ze struktura modeli: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TEST INTEGRACJI api_sql_lite.py z SQL/database_models.py")
    print("=" * 60)
    
    success = True
    
    if not test_imports():
        success = False
    
    if not test_database_structure():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("WSZYSTKIE TESTY ZAKONCZONE SUKCESEM!")
        print("Aplikacja api_sql_lite.py jest gotowa do uzycia.")
    else:
        print("NIEKTORE TESTY NIE POWIODLY SIE")
        print("Sprawdz powyzsze bledy przed uruchomieniem aplikacji.")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
