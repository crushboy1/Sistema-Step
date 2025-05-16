from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
from functools import wraps
from lxml import etree

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Cambia esta clave para producción

API_URL = "http://35.224.173.52:5000/user_service/user/login"

# URL de la API de proyectos
PROJECTS_URL = "http://35.224.173.52:5000/project_service_rest/projects"

soap_service_url = "http://35.224.173.52:5000/project_service_soap/project_service_soap"
# soap_service_url = "http://26.130.56.255:5004"


RECAPTCHA_SITE_KEY = "6LcJV4QqAAAAAOwGW-qWQe0OOWQnWTKJIQbaz-q2"
RECAPTCHA_SECRET_KEY = "6LcJV4QqAAAAAImYdda4CJFkgy4HZ8yP3-c46d3H"

@app.route('/')
def index():
    if 'token' in session:
        return f"Usuario autenticado con token: {session['token']}"
    return redirect(url_for('login'))



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            flash('Inicia sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function



# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         recaptcha_response = request.form['g-recaptcha-response']

#         # Verificar el reCAPTCHA con la API de Google
#         recaptcha_payload = {'secret': RECAPTCHA_SECRET_KEY, 'response': recaptcha_response}
#         recaptcha_res = requests.post("https://www.google.com/recaptcha/api/siteverify", data=recaptcha_payload)
#         recaptcha_result = recaptcha_res.json()

#         if not recaptcha_result.get('success'):
#             flash('Error de reCAPTCHA. Por favor verifica que no eres un robot.', 'danger')
#             return render_template('login.html', recaptcha_site_key=RECAPTCHA_SITE_KEY)
        

#         # Enviar datos al API
#         payload = {"email": email, "contrasena": password}
#         response = requests.post(API_URL, json=payload)

#         if response.status_code == 200:
#             data = response.json()
#             session['token'] = data['token']  # Guardar el token en la sesión
#             flash('Inicio de sesión exitoso', 'success')
#             return redirect(url_for('dashboard'))
#         else:
#             flash('Credenciales incorrectas', 'danger')

#     return render_template('login.html', recaptcha_site_key=RECAPTCHA_SITE_KEY)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        recaptcha_response = request.form['g-recaptcha-response']

        # Verificar el reCAPTCHA con la API de Google
        recaptcha_payload = {'secret': RECAPTCHA_SECRET_KEY, 'response': recaptcha_response}
        recaptcha_res = requests.post("https://www.google.com/recaptcha/api/siteverify", data=recaptcha_payload)
        recaptcha_result = recaptcha_res.json()

        if not recaptcha_result.get('success'):
            flash('Error de reCAPTCHA. Por favor verifica que no eres un robot.', 'danger')
            return render_template('login.html', recaptcha_site_key=RECAPTCHA_SITE_KEY)

        # Enviar datos al API
        payload = {"email": email, "contrasena": password}
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            data = response.json()

            # Guardar el token y la información del usuario en la sesión
            session['token'] = data.get('token')  # Guardar el token
            session['user'] = data.get('user')  # Guardar los datos del usuario (email, id_usuario, nombre)

            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('dashboard'))  # Redirigir al dashboard
        else:
            # Obtener el mensaje de error del API (si está disponible)
            error_message = response.json().get('message', 'Credenciales incorrectas.')
            flash(error_message, 'danger')

    return render_template('login.html', recaptcha_site_key=RECAPTCHA_SITE_KEY)




# Página principal del dashboard
@app.route('/dashboard')
def dashboard():
    if 'token' not in session:
        return redirect(url_for('login'))  # Redirigir al login si no hay token

    # Obtener el token JWT desde la sesión
    token = session['token']
    headers = {'Authorization': f'Bearer {token}'}  # Enviar el token en los encabezados

    # Consumir la API REST de proyectos usando el token JWT
    response = requests.get(PROJECTS_URL, headers=headers)

    # Depuración: Imprimir el código de respuesta y el contenido de la respuesta
    print(f"Respuesta del servidor: {response.status_code}")
    print(f"Datos devueltos: {response.json()}")

    if response.status_code == 200:
        projects = response.json()  # Obtener los proyectos en formato JSON
        # Asegúrate de que los datos se pasan correctamente a la plantilla
        return render_template('dashboard.html', projects=projects)
    else:
        return render_template('dashboard.html', error='Error al obtener los proyectos')


# @app.route("/proyecto/nuevo", methods=["GET", "POST"])
# def nuevo_proyecto():
#     if "token" not in session:
#         flash("Por favor, inicia sesión para continuar.", "warning")
#         return redirect(url_for("login"))

#     if request.method == "POST":
#         # Captura datos del formulario
#         nombre = request.form.get("nombre")
#         descripcion = request.form.get("descripcion")
#         id_admin = request.form.get("id_admin")

#         # Construir el mensaje SOAP
#         soap_payload = f"""
#         <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:proj="project_service.soap">
#            <soapenv:Header/>
#            <soapenv:Body>
#               <proj:register_project>
#                  <proj:nombre>{nombre}</proj:nombre>
#                  <proj:descripcion>{descripcion}</proj:descripcion>
#                  <proj:id_admin>{id_admin}</proj:id_admin>
#               </proj:register_project>
#            </soapenv:Body>
#         </soapenv:Envelope>
#         """

#         # Recuperar el token desde la sesión
#         token = session["token"]

#         # Configurar los encabezados
#         headers = {
#             "Content-Type": "text/xml; charset=utf-8",
#             "Authorization": f"Bearer {token}",
#         }

#         # Enviar la solicitud al servicio SOAP
#         try:
#             response = requests.post(soap_service_url, data=soap_payload, headers=headers)

#             if response.status_code == 200:
#                 flash("Proyecto registrado exitosamente.", "success")
#                 return redirect(url_for("nuevo_proyecto"))
#             else:
#                 flash(f"Error en la solicitud: {response.status_code} - {response.text}", "danger")
#         except Exception as e:
#             flash(f"Error al conectar con el servicio SOAP: {str(e)}", "danger")

#     return render_template("nuevo_proyecto.html")


@app.route("/proyecto/nuevo", methods=["GET", "POST"])
def nuevo_proyecto():
    if "token" not in session or "user" not in session:
        flash("Por favor, inicia sesión para continuar.", "warning")
        return redirect(url_for("login"))

    # Obtener la ID del administrador (id_usuario) desde la sesión
    user = session["user"]
    id_admin = user["id_usuario"]

    if request.method == "POST":
        # Captura datos del formulario
        nombre = request.form.get("nombre")
        descripcion = request.form.get("descripcion")

        # Construir el mensaje SOAP
        soap_payload = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:proj="project_service.soap">
           <soapenv:Header/>
           <soapenv:Body>
              <proj:register_project>
                 <proj:nombre>{nombre}</proj:nombre>
                 <proj:descripcion>{descripcion}</proj:descripcion>
                 <proj:id_admin>{id_admin}</proj:id_admin>
              </proj:register_project>
           </soapenv:Body>
        </soapenv:Envelope>
        """

        # Recuperar el token desde la sesión
        token = session["token"]

        # Configurar los encabezados
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "Authorization": f"Bearer {token}",
        }

        # Enviar la solicitud al servicio SOAP
        try:
            response = requests.post(soap_service_url, data=soap_payload, headers=headers)

            if response.status_code == 200:
                flash("Proyecto registrado exitosamente.", "success")
                return redirect(url_for("dashboard"))
            else:
                flash(f"Error en la solicitud: {response.status_code} - {response.text}", "danger")
        except Exception as e:
            flash(f"Error al conectar con el servicio SOAP: {str(e)}", "danger")

    return render_template("nuevo_proyecto.html", id_admin=id_admin)



@app.route("/proyecto/eliminar/<int:project_id>", methods=["POST"])
@login_required
def eliminar_proyecto(project_id):
    # Recuperar el token desde la sesión
    token = session["token"]

    # Construir el mensaje SOAP para eliminar el proyecto
    soap_payload = f"""
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:proj="project_service.soap">
       <soapenv:Header/>
       <soapenv:Body>
          <proj:delete_project>
             <proj:project_id>{project_id}</proj:project_id>
          </proj:delete_project>
       </soapenv:Body>
    </soapenv:Envelope>
    """

    # Configurar los encabezados de la solicitud SOAP
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "Authorization": f"Bearer {token}",
    }

    try:
        # Enviar la solicitud SOAP para eliminar el proyecto
        response = requests.post(soap_service_url, data=soap_payload, headers=headers)

        # Verificar la respuesta
        if response.status_code == 200:
            flash(f"Proyecto con ID {project_id} eliminado exitosamente.", "success")
        else:
            flash(f"Error al eliminar el proyecto: {response.status_code} - {response.text}", "danger")
    except Exception as e:
        flash(f"Error al conectar con el servicio SOAP: {str(e)}", "danger")

    # Redirigir de vuelta al dashboard
    return redirect(url_for("dashboard"))




@app.route('/logout')
def logout():
    session.pop('token', None)  # Eliminar el token de la sesión
    flash('Cierre de sesión exitoso', 'success')
    return redirect(url_for('login'))



# Configurar el puerto y host para ejecutar el servidor Flask
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
