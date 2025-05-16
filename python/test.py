import requests
import json
import requests

url = "http://127.0.0.1:8000/api/register"  # O el endpoint correspondiente
data = {
        "nombre": "test",
        "email": "test@aea.com",
        "contraseña": "123",
        "contraseña_confirmation": "123"
    }

response = requests.post(url, json=data)

print("Código de estado:", response.status_code)
print("Respuesta completa:", response.text)
