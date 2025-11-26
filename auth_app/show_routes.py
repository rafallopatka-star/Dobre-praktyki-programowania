

from main import app

print("="*50)
print("DOSTĘPNE ENDPOINTY W AUTH_APP")
print("="*50)

for route in app.routes:
    if hasattr(route, 'path'):
        methods = ','.join(route.methods) if hasattr(route, 'methods') else 'GET'
        print(f"{methods:15} {route.path}")

print("="*50)
