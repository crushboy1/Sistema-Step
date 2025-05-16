import requests

# URL del servicio SOAP
url = 'http://localhost:8000/api/soap'

def get_estudiantes():
    # Cuerpo de la solicitud SOAP para obtener estudiantes
    soap_request = """<?xml version="1.0" encoding="UTF-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
            <getEstudiantes xmlns="http://localhost:8000/api/soap"/>
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
        print("Respuesta del servidor (Estudiantes):")
        print(response.text)
    else:
        print(f"Error al obtener estudiantes: {response.status_code}")
        print(response.text)

def crear_estudiante(nombre, apellido, edad):
    # Cuerpo de la solicitud SOAP para crear un nuevo estudiante
    soap_request = f"""<?xml version="1.0" encoding="UTF-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
            <crearEstudiante xmlns="http://localhost:8000/api/soap">
                <nombre>{nombre}</nombre>
                <apellido>{apellido}</apellido>
                <edad>{edad}</edad>
            </crearEstudiante>
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
        print("Respuesta del servidor (Crear Estudiante):")
        print(response.text)
    else:
        print(f"Error al crear estudiante: {response.status_code}")
        print(response.text)

# Ejemplo de uso
if __name__ == "__main__":
    # Obtener la lista de estudiantes
    get_estudiantes()

    # Crear un nuevo estudiante
    crear_estudiante("Frank", "Torres", 22)
