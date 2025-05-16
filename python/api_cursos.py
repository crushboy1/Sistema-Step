import requests

# URL base del API
URL_BASE = "http://127.0.0.1:8000/api/v1/cursos"

# Función para obtener todos los cursos
def obtener_cursos():
    response = requests.get(URL_BASE)
    if response.status_code == 200:
        cursos = response.json()
        print("Cursos:", cursos)
    else:
        print(f"Error al obtener cursos: {response.status_code}, {response.text}")

# Función para crear un curso
def crear_curso(nombre, descripcion, creditos):
    nuevo_curso = {
        "nombre": nombre,
        "descripcion": descripcion,
        "creditos": creditos,
    }
    response = requests.post(URL_BASE, json=nuevo_curso)
    if response.status_code == 201:
        print("Curso creado:", response.json())
    else:
        print(f"Error al crear curso: {response.status_code}, {response.text}")

# Función para actualizar un curso
def actualizar_curso(id_curso, nombre=None, descripcion=None, creditos=None):
    curso_actualizado = {
        "nombre": nombre,
        "descripcion": descripcion,
        "creditos": creditos,
    }
    curso_actualizado = {k: v for k, v in curso_actualizado.items() if v is not None}
    response = requests.put(f"{URL_BASE}/{id_curso}", json=curso_actualizado)
    if response.status_code == 200:
        print("Curso actualizado:", response.json())
    else:
        print(f"Error al actualizar curso: {response.status_code}, {response.text}")

# Función para eliminar un curso
def eliminar_curso(id_curso):
    response = requests.delete(f"{URL_BASE}/{id_curso}")
    if response.status_code == 200:
        print("Curso eliminado")
    else:
        print(f"Error al eliminar curso: {response.status_code}, {response.text}")

# Ejecución del programa
if __name__ == "__main__":
    print("Obteniendo cursos...")
    obtener_cursos()

    print("\nCreando un curso...")
    crear_curso("Matemáticas", "Curso de matemáticas avanzadas", 10)

    print("\nActualizando un curso...")
    actualizar_curso(3, "Matemáticas Básicas", "Curso de matemáticas para principiantes", 3)

    print("\nEliminando un curso...")
    eliminar_curso(12)
