import requests

# URL del servicio SOAP
url = 'http://localhost:8000/api/soap'

def get_cursos():
    # Cuerpo de la solicitud SOAP para obtener cursos
    soap_request = """<?xml version="1.0" encoding="UTF-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
            <getCursos xmlns="http://localhost:8000/api/soap"/>
        </soap:Body>
    </soap:Envelope>"""

    # Encabezados de la solicitud
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
    }

    # Enviar la solicitud POST
    response = requests.post(url, data=soap_request, headers=headers)

    # Verificar el código de estado de la respuesta
    if response.status_code == 200:
        print("Respuesta del servidor (Cursos):")
        print(response.text)
    else:
        print(f"Error al obtener cursos: {response.status_code}")
        print(response.text)

def crear_curso(nombre, descripcion, creditos):
    # Cuerpo de la solicitud SOAP para crear un nuevo curso
    soap_request = f"""<?xml version="1.0" encoding="UTF-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
            <crearCurso xmlns="http://localhost:8000/api/soap">
                <nombre>{nombre}</nombre>
                <descripcion>{descripcion}</descripcion>
                <creditos>{creditos}</creditos>
            </crearCurso>
        </soap:Body>
    </soap:Envelope>"""

    # Encabezados de la solicitud
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
    }

    # Enviar la solicitud POST
    response = requests.post(url, data=soap_request, headers=headers)

    # Verificar el código de estado de la respuesta
    if response.status_code == 200:
        print("Respuesta del servidor (Crear Curso):")
        print(response.text)
    else:
        print(f"Error al crear curso: {response.status_code}")
        print(response.text)

# Ejemplo de uso
if __name__ == "__main__":
    # Obtener la lista de cursos
    get_cursos()

    # Crear un nuevo curso
    crear_curso("historia", "pizarro", 2)
