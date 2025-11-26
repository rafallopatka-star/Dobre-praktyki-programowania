

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, shell=False):
    """Uruchamia polecenie i zwraca wynik"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("=" * 70)
    print("SETUP APLIKACJI UWIERZYTELNIANIA FASTAPI")
    print("=" * 70 + "\n")
    
    
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    print(f"Katalog: {script_dir}\n")
    
    
    print("✓ Sprawdzenie środowiska Python...")
    try:
        import fastapi
        import sqlalchemy
        import pydantic
        import jwt
        import bcrypt
        print("✓ Wszystkie wymagane pakiety są zainstalowane\n")
    except ImportError as e:
        print(f"⚠ Brak pakietu: {e}")
        print("Instaluję brakujące pakiety...\n")
        packages = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "pydantic",
            "pyjwt",
            "bcrypt",
            "python-multipart",
            "requests"
        ]
        success, _, _ = run_command(f"{sys.executable} -m pip install {' '.join(packages)}")
        if success:
            print("✓ Pakiety zainstalowane\n")
        else:
            print("✗ Błąd przy instalacji pakietów\n")
            return
    
    # Check database
    db_file = script_dir / "auth.db"
    if db_file.exists():
        print(f"✓ Baza danych istnieje: {db_file}")
        response = input("  Czy chcesz usunąć i stworzyć nową bazę? (y/n): ").strip().lower()
        if response == 'y':
            db_file.unlink()
            print("  Baza danych usunięta\n")
        else:
            print()
    else:
        print("✓ Baza danych będzie stworzona automatycznie\n")
    
    # Show quick start
    print("=" * 70)
    print("INSTRUKCJE URUCHOMIENIA")
    print("=" * 70 + "\n")
    
    print("1️⃣  Uruchomienie serwera:")
    print("   python -m uvicorn main:app --reload\n")
    
    print("2️⃣  Dostęp do aplikacji:")
    print("   http://127.0.0.1:8000\n")
    
    print("3️⃣  Swagger UI (dokumentacja API):")
    print("   http://127.0.0.1:8000/docs\n")
    
    print("4️⃣  Domyślne konto admin:")
    print("   Username: admin")
    print("   Password: admin123")
    print("   Rola: admin\n")
    
    print("5️⃣  Uruchomienie testów:")
    print("   python test_auth_api.py\n")
    
    print("=" * 70)
    print("Czy chcesz teraz uruchomić serwer? (y/n): ", end="")
    
    if input().strip().lower() == 'y':
        print("\n🚀 Uruchamianie serwera...\n")
        subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload"])
    else:
        print("\n✓ Setup gotowy! Uruchom serwer ręcznie:\n")
        print("   python -m uvicorn main:app --reload\n")

if __name__ == "__main__":
    main()
