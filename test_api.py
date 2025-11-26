"""
Skrypt testowy - porównanie wydajności CSV vs SQLite
"""
import time
import requests

def test_endpoint(url, name):
    print(f"\nTestowanie: {name}")
    start = time.time()
    response = requests.get(url)
    end = time.time()
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Sukces - Pobrano {len(data)} rekordów")
        print(f"⏱ Czas: {end - start:.3f} sekund")
    else:
        print(f"✗ Błąd: {response.status_code}")

if __name__ == '__main__':
    print("="*50)
    print("TEST ENDPOINTÓW API")
    print("="*50)
    print("\nUpewnij się, że serwer działa na http://127.0.0.1:5000")
    print("Uruchom: python api_sql_lite.py")
    
    input("\nNaciśnij Enter aby rozpocząć test...")
    
    base_url = "http://127.0.0.1:5000"
    
    test_endpoint(f"{base_url}/movies", "Movies")
    test_endpoint(f"{base_url}/links", "Links")
    test_endpoint(f"{base_url}/ratings", "Ratings")
    test_endpoint(f"{base_url}/tags", "Tags")
    
    print("\n" + "="*50)
    print("Test zakończony!")
    print("="*50)
