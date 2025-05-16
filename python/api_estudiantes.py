import requests

# URL base de la API
URL_BASE_ESTUDIANTES = "http://127.0.0.1:8000/api/v1/estudiantes"

# Función para obtener la lista de estudiantes
def obtener_estudiantes():
    response = requests.get(URL_BASE_ESTUDIANTES)
    if response.status_code == 200:
        estudiantes = response.json()
        print("Estudiantes:", estudiantes)
    else:
        print(f"Error al obtener estudiantes: {response.status_code}, {response.text}")

# Función para crear un nuevo estudiante
def crear_estudiante(nombre, apellido, edad):
    nuevo_estudiante = {
        "nombre": nombre,
        "apellido": apellido,
        "edad": edad,
    }
    response = requests.post(URL_BASE_ESTUDIANTES, json=nuevo_estudiante)
    if response.status_code == 201:
        print("Estudiante creado:", response.json())
    else:
        print(f"Error al crear estudiante: {response.status_code}, {response.text}")

# Función para obtener un estudiante específico por ID
def obtener_estudiante(id_estudiante):
    response = requests.get(f"{URL_BASE_ESTUDIANTES}/{id_estudiante}")
    if response.status_code == 200:
        print("Estudiante encontrado:", response.json())
    elif response.status_code == 404:
        print(f"Estudiante {id_estudiante} no encontrado.")
    else:
        print(f"Error al obtener estudiante: {response.status_code}, {response.text}")

# Función para actualizar un estudiante
def actualizar_estudiante(id_estudiante, nombre=None, apellido=None, edad=None):
    estudiante_actualizado = {
        "nombre": nombre,
        "apellido": apellido,
        "edad": edad,
    }
    # Eliminar valores `None` para no enviar datos innecesarios
    estudiante_actualizado = {k: v for k, v in estudiante_actualizado.items() if v is not None}
    response = requests.put(f"{URL_BASE_ESTUDIANTES}/{id_estudiante}", json=estudiante_actualizado)
    if response.status_code == 200:
        print("Estudiante actualizado:", response.json())
    elif response.status_code == 404:
        print(f"Estudiante con ID {id_estudiante} no encontrado.")
    else:
        print(f"Error al actualizar estudiante: {response.status_code}, {response.text}")

# Función para eliminar un estudiante
def eliminar_estudiante(id_estudiante):
    response = requests.delete(f"{URL_BASE_ESTUDIANTES}/{id_estudiante}")
    if response.status_code == 200:
        print(f"Estudiante {id_estudiante} eliminado.")
    elif response.status_code == 404:
        print(f"Estudiante {id_estudiante} no encontrado.")
    else:
        print(f"Error al eliminar estudiante: {response.status_code}, {response.text}")

# Ejecución del programa
if __name__ == "__main__":
    print("Obteniendo estudiantes...")
    obtener_estudiantes()

    print("\nCreando un estudiante...")
    crear_estudiante("Fracisco", "Pizarro", 490)

    print("\nObteniendo un estudiante  específico...")
    obtener_estudiante(10)

    print("\nActualizando un estudiante...")
    actualizar_estudiante(31, nombre="El chavo", apellido="del 8", edad=85)

    print("\nEliminando un estudiante...")
    eliminar_estudiante(18)
