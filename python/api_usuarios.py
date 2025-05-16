import requests

# URL base de la API
BASE_URL = "http://127.0.0.1:8000/api"

# Registrar un nuevo usuario
def register_user(nombre, email, contraseña, confirmacion_contraseña):
    payload = {
        "nombre": nombre,
        "email": email,
        "contraseña": contraseña,
        "contraseña_confirmation": confirmacion_contraseña
    }
    response = requests.post(f"{BASE_URL}/register", json=payload)
    return response.json()

# Iniciar sesión
def login_user(email, contraseña):
    payload = {
        "email": email,
        "contraseña": contraseña,
        "contraseña_confirmation": contraseña
    }
    response = requests.post(f"{BASE_URL}/login", json=payload)
    return response.json()

# Cerrar sesión
def logout_user(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/logout", headers=headers)
    return response.json()

# Obtener detalles del usuario autenticado
def get_user_details(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/user", headers=headers)
    return response.json()

# Actualizar información de usuario
def update_user(token, user_id, nombre=None, email=None, contraseña=None, confirmacion_contraseña=None):
    payload = {}
    if nombre:
        payload["nombre"] = nombre
    if email:
        payload["email"] = email
    if contraseña:
        payload["contraseña"] = contraseña
        payload["contraseña_confirmation"] = confirmacion_contraseña

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{BASE_URL}/user/{user_id}", json=payload, headers=headers)
    return response.json()

# Eliminar un usuario
def delete_user(token, user_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/user/{user_id}", headers=headers)
    return response.json()

# Ejemplo de uso
if __name__ == "__main__":
    # Registrar un usuario
    registro = register_user("Juan Pérez", "juan@example.com", "password123", "password123")
    print("Registro:", registro)

    # Iniciar sesión
    inicio_sesion = login_user("juan@example.com", "password123")
    print("Inicio de sesión:", inicio_sesion)

    if "token" in inicio_sesion:
        token = inicio_sesion["token"]

        # Obtener detalles del usuario autenticado
        detalles = get_user_details(token)
        print("Detalles del usuario:", detalles)

        # Actualizar información del usuario
        actualizacion = update_user(token, detalles["id"], nombre="Juan Actualizado")
        print("Actualización del usuario:", actualizacion)

        # Cerrar sesión
        cierre_sesion = logout_user(token)
        print("Cierre de sesión:", cierre_sesion)
