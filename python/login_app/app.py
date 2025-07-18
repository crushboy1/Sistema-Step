from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import requests
import zeep  # Aunque zeep no se usa directamente en tu código actual, lo mantengo por si es una dependencia futura para SOAP
import json
import re
import os
from urllib.parse import urlparse
from datetime import datetime
import pytz
import logging # Nueva importación para logging

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Configurar un logger básico para Flask
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app.logger.setLevel(logging.INFO) # Nivel de logging para la aplicación Flask

API_URL = os.environ.get("LARAVEL_API_URL", "http://localhost:8000/api")
API_URL_BASE = os.environ.get("LARAVEL_API_BASE_URL", "http://localhost:8000/api/v1")

# URLs para los servicios SOAP (asumiendo que están configurados en Laravel)
# Ajusta estas URLs si tus endpoints SOAP son diferentes
WEB_URL = os.environ.get("LARAVEL_SOAP_URL", "http://localhost:8000/api/v1/soap/estudiantes") # Asumo endpoint de estudiantes SOAP
WEB_URL_BASE = os.environ.get("LARAVEL_SOAP_CURSOS_URL", "http://localhost:8000/api/v1/soap/cursos") # Asumo endpoint de cursos SOAP

RECAPTCHA_SITE_KEY = '6Ld6ey0rAAAAAJp4boxN3CzM-VjsPKjK-bZLVPiU'
RECAPTCHA_SECRET_KEY = '6Ld6ey0rAAAAANZkkDMFnTkcLRfA5R2skbv5LXBQ'

# --- Helper para verificar roles en Jinja2 ---
def has_role_helper(user_data, role_name):
    """Verifica si un usuario tiene un rol específico."""
    if not user_data or not isinstance(user_data, dict):
        return False
    if 'roles' not in user_data or not user_data['roles']:
        return False
    return any(role.get('name') == role_name for role in user_data['roles'])

# Añadir la función al contexto de Jinja2 para que esté disponible en todas las plantillas
app.jinja_env.globals.update(has_role=has_role_helper)

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y %H:%M'):
    if not value:
        return "N/A"
    try:
        # Intentar parsear el formato ISO 8601 con microsegundos y 'Z'
        dt_object = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        try:
            # Si falla, intentar parsear sin microsegundos
            dt_object = datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            # Si falla de nuevo, intentar parsear solo la fecha si es necesario
            try:
                dt_object = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                return value # Retornar el valor original si no se puede parsear
    return dt_object.strftime(format)

VALIDATION_MESSAGES_ES = {
    "The :attribute field is required.": "El campo :attribute es obligatorio.",
    "The :attribute field must be a valid email address.": "El campo :attribute debe ser una dirección de correo electrónico válida.",
    "The :attribute has already been taken.": "El :attribute ya ha sido registrado.",
    "The :attribute field confirmation does not match.": "La confirmación del campo :attribute no coincide.",
    "The password field must be at least :min characters.": "El campo contraseña debe tener al menos :min caracteres.",
    "The name field is required.": "El campo nombre completo es obligatorio.",
    "The password field is required.": "El campo contraseña es obligatorio.",
    "nombre": "nombre completo",
    "contraseña": "contraseña",
    "email": "correo electrónico",
    "password": "contraseña",
    "password_confirmation": "confirmación de contraseña",
    "name": "nombre completo",
}

def translate_validation_message(message, field_name=None):
    translated_message = VALIDATION_MESSAGES_ES.get(message, message)

    if ':min' in translated_message:
        match = re.search(r'at least (\d+) characters', message)
        if match:
            min_chars = match.group(1)
            translated_message = translated_message.replace(':min', min_chars)

    if ':attribute' in translated_message and field_name:
        translated_field_name = VALIDATION_MESSAGES_ES.get(field_name, field_name)
        translated_message = translated_message.replace(':attribute', translated_field_name)

    return translated_message

# Helper function to validate URLs (MISSING - AÑADIDA AQUÍ)
def is_valid_url(url):
    if not isinstance(url, str):
        return False
    try:
        result = urlparse(url)
        # Verifica que tenga un esquema (http/https) y un dominio
        return all([result.scheme in ['http', 'https'], result.netloc])
    except ValueError:
        return False

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        recaptcha_response = request.form.get("g-recaptcha-response")

        # 1. Verificar reCAPTCHA
        recaptcha_data = {
            'secret': RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'

        try:
            recaptcha_verify_response = requests.post(verify_url, data=recaptcha_data)
            recaptcha_result = recaptcha_verify_response.json()

            if not recaptcha_result.get('success'):
                flash("Error de CAPTCHA. Por favor, intenta nuevamente.", "danger")
                return redirect(url_for("login"))
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión con el servicio reCAPTCHA: {e}", "danger")
            return redirect(url_for("login"))
        except json.JSONDecodeError:
            flash("Error al procesar la respuesta de reCAPTCHA.", "danger")
            return redirect(url_for("login"))

        # 2. Login con Laravel API
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        payload = {"email": email, "password": password}

        try:
            api_response = requests.post(f"{API_URL}/login", headers=headers, json=payload)
            api_data = api_response.json()

            app.logger.info(f"API Response Status Code (Login): {api_response.status_code}")
            app.logger.debug(f"API Response Content (Login): {api_response.text}")

            if api_response.status_code == 200:
                token = api_data.get("token")
                requires_2fa = api_data.get("requires_2fa", False)

                if requires_2fa:
                    session['email_for_2fa'] = api_data.get('email', email)
                    session.pop('token', None)
                    session.pop('user', None)
                    flash("Se ha enviado un código de verificación a su correo para completar el inicio de sesión.", "info")
                    return redirect(url_for("verify_2fa"))
                else:
                    if token:
                        session['token'] = token
                        user_info_headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
                        user_info_response = requests.get(f"{API_URL}/user", headers=user_info_headers)

                        if user_info_response.status_code == 200:
                            session['user'] = user_info_response.json()
                            flash("Inicio de sesión exitoso.", "success")
                            return redirect(url_for("cursos"))
                        else:
                            flash("Error al obtener la información de su perfil. Por favor, intente de nuevo.", "danger")
                            session.pop('token', None)
                            return redirect(url_for("login"))
                    else:
                        flash("Error inesperado: no se recibió token de autenticación.", "danger")
                        return redirect(url_for("login"))

            elif api_response.status_code == 401:
                flash(api_data.get("message", "Credenciales inválidas."), "danger")
                return redirect(url_for("login"))
            else:
                flash(api_data.get("message", f"Error desconocido al iniciar sesión (Código: {api_response.status_code})."), "danger")
                return redirect(url_for("login"))

        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión con la API de Laravel: {e}", "danger")
            return redirect(url_for("login"))
        except json.JSONDecodeError:
            flash(f"Error al procesar la respuesta de la API de Laravel (Código: {api_response.status_code}).", "danger")
            return redirect(url_for("login"))

    return render_template("login.html", recaptcha_site_key=RECAPTCHA_SITE_KEY)


@app.route("/verify-2fa", methods=["GET", "POST"])
def verify_2fa():
    if 'email_for_2fa' not in session:
        flash("Acceso denegado. Por favor, inicie sesión primero para verificar su cuenta.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        verification_code = request.form.get("verification_code")
        email = session.get('email_for_2fa')

        if not email:
            flash("Error en el proceso de verificación. Por favor, inicie sesión nuevamente.", "danger")
            return redirect(url_for("login"))

        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        payload = {"email": email, "two_factor_code": verification_code}

        try:
            api_response = requests.post(f"{API_URL}/verifyCode", headers=headers, json=payload)
            api_data = api_response.json()

            app.logger.info(f"Verify 2FA API Response Status Code: {api_response.status_code}")
            app.logger.debug(f"Verify 2FA API Response Content: {api_response.text}")

            if api_response.status_code == 200:
                token = api_data.get("token")
                user = api_data.get("user")

                if token:
                    session['token'] = token
                    if user:
                        session['user'] = user
                    else:
                        user_info_headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
                        user_info_response = requests.get(f"{API_URL}/user", headers=user_info_headers)

                        if user_info_response.status_code == 200:
                            session['user'] = user_info_response.json()
                        else:
                            flash("Error al obtener la información de su perfil después de la verificación 2FA.", "danger")
                            session.clear()
                            return redirect(url_for("login"))

                    session.pop('email_for_2fa', None)

                    flash("Código verificado exitosamente. Inicio de sesión completo.", "success")
                    return redirect(url_for("cursos"))
                else:
                    flash("Error inesperado: no se recibió token de autenticación.", "danger")
                    session.clear()
                    return redirect(url_for("login"))
            else:
                flash(api_data.get("message", f"Error al verificar el código (Código: {api_response.status_code})."), "danger")
                return render_template("verify_2fa.html", email=email)

        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión con la API de Laravel: {e}", "danger")
            return redirect(url_for("verify_2fa"))
        except json.JSONDecodeError:
            flash(f"Error al procesar la respuesta de verificación de la API de Laravel (Código: {api_response.status_code}).", "danger")
            return redirect(url_for("verify_2fa"))

    email_for_2fa = session.get('email_for_2fa', '')
    return render_template("verify_2fa.html", email=email_for_2fa)


@app.route("/resend-2fa-code", methods=["POST"])
def resend_2fa_code():
    """
    Reenvía el código 2FA al usuario.
    """
    if 'email_for_2fa' not in session:
        flash("Acceso denegado. Por favor, inicie sesión primero.", "warning")
        return redirect(url_for("login"))

    email = session.get('email_for_2fa')
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = {"email": email}

    try:
        api_response = requests.post(f"{API_URL}/resendCode", headers=headers, json=payload)
        api_data = api_response.json()

        if api_response.status_code == 200:
            flash("Se ha reenviado un nuevo código de verificación a su correo.", "info")
        else:
            flash(api_data.get("message", "Error al reenviar el código."), "danger")

    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {e}", "danger")
    except json.JSONDecodeError:
        flash("Error al procesar la respuesta del servidor.", "danger")

    return redirect(url_for("verify_2fa"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        last_name = request.form.get("last_name")
        number = request.form.get("number")
        email = request.form.get("email")
        role = request.form.get("role")
        password = request.form.get("password")
        password_confirmation = request.form.get("password_confirmation")
        recaptcha_response = request.form.get("g-recaptcha-response")

        data = {
            'secret': RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        response = requests.post(verify_url, data=data)
        result = response.json()

        if result.get('success'):
            api_response = requests.post(f"{API_URL}/register", json={
                "name": name,
                "last_name": last_name,
                "number": number,
                "email": email,
                "role": role,
                "password": password,
                "password_confirmation": password_confirmation
            })

            app.logger.info(f"Register API Response Status Code: {api_response.status_code}")
            app.logger.debug(f"Register API Response Content: {api_response.text}")

            if api_response.status_code == 201:
                flash("Registro exitoso, por favor inicia sesión.", "success")
                return redirect(url_for("login"))

            elif api_response.status_code == 422:
                try:
                    api_data = api_response.json()
                    error_message = "Errores de validación:"

                    if 'errors' in api_data:
                        for field, messages in api_data['errors'].items():
                            translated_messages = [translate_validation_message(msg, field) for msg in messages]
                            error_message += f"\n- {translate_validation_message(field)}: {', '.join(translated_messages)}"
                    else:
                        error_message = translate_validation_message(api_data.get("message", f"Error de validación desconocido (Código: {api_response.status_code})."))

                    flash(error_message, "danger") # Cambiado de 'error' a 'danger'

                except json.JSONDecodeError:
                    flash(f"Error al procesar errores de validación de la API (Código: 422, respuesta no JSON).", "danger") # Cambiado de 'error' a 'danger'

                return redirect(url_for("register"))

            else:
                try:
                    api_data = api_response.json()
                    error_message = api_data.get("message", f"Error al registrar usuario (Código: {api_response.status_code})")
                    flash(error_message, "danger") # Cambiado de 'error' a 'danger'

                except json.JSONDecodeError:
                    flash(f"Error al procesar la respuesta de registro de la API (Código: {api_response.status_code}).", "danger") # Cambiado de 'error' a 'danger'

                return redirect(url_for("register"))

        else:
            flash("Error de CAPTCHA. Por favor, intenta nuevamente.", "danger") # Cambiado de 'error' a 'danger'
            return redirect(url_for("register"))

    return render_template("register.html", recaptcha_site_key=RECAPTCHA_SITE_KEY)

@app.route("/estudiantes", methods=["GET"])
def estudiantes():
    if 'token' not in session:
        flash("Por favor, inicia sesión.", "warning")
        return redirect(url_for("login"))

    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}

    query = request.args.get("q", "").strip().lower()

    response = requests.get(f"{API_URL_BASE}/estudiantes", headers=headers)

    if response.status_code == 200:
        try:
            estudiantes = response.json()
            # Cambio aquí: Obtener el nombre del usuario de la sesión correctamente
            user_name = session.get('user', {}).get('name', 'Usuario')

            now = datetime.now()
            current_date = now.strftime("%d/%m/%Y")
            current_time = now.strftime("%I:%M:%S %p")

            if query:
                estudiantes = [
                    est for est in estudiantes
                    if query in est.get("nombre", "").lower() or query in est.get("apellido", "").lower()
                ]
            return render_template("estudiantes.html", estudiantes=estudiantes, user_name=user_name, current_date=current_date, current_time=current_time)
        except json.JSONDecodeError:
            flash("Error al procesar la lista de estudiantes recibida de la API.", "danger")
            return redirect(url_for("home"))


    else:
        if response.status_code == 401:
            flash("Su sesión ha expirado. Por favor, inicie sesión nuevamente.", "warning")
            session.pop('token', None)
            session.pop('email_for_2fa', None)
            session.pop('user', None) # Limpiar el usuario también
            return redirect(url_for("login"))
        else:
            try:
                api_data = response.json()
                flash(api_data.get("message", f"Error al cargar los estudiantes (Código: {response.status_code})."), "danger")
            except json.JSONDecodeError:
                 flash(f"Error al cargar los estudiantes (Código: {response.status_code}, respuesta no JSON).", "danger")

            return redirect(url_for("home"))



@app.route("/estudiantes/nuevo", methods=["GET", "POST"])
def nuevo_estudiante():
    if 'token' not in session:
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("login"))

    token = session['token']
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "text/xml"} # Headers para SOAP

    if request.method == "POST":
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        edad = request.form.get("edad")

        payload = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:App\Http\Controllers">
           <soapenv:Header/>
           <soapenv:Body>
              <urn:crearEstudiante>
                 <nombre>{nombre}</nombre>
                 <apellido>{apellido}</apellido>
                 <edad>{edad}</edad>
              </urn:crearEstudiante>
           </soapenv:Body>
        </soapenv:Envelope>
        """
        app.logger.debug(f"SOAP Payload enviado a {WEB_URL}: {payload}")

        try:
            response = requests.post(WEB_URL, headers=headers, data=payload)
            app.logger.info(f"SOAP Response Status Code: {response.status_code}")
            app.logger.debug(f"SOAP Response Content: {response.text}")

            if response.status_code == 200:
                if "id" in response.text: # Una validación muy básica de la respuesta SOAP
                    flash("Estudiante creado con éxito.", "success")
                    return redirect(url_for("estudiantes"))
                else:
                    flash("Error al crear el estudiante. Verifica los datos o la respuesta del servicio SOAP.", "danger")
            else:
                flash(f"Error al conectar con el servicio SOAP. Código de estado: {response.status_code}. Respuesta: {response.text[:200]}...", "danger")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión con el servicio SOAP: {e}", "danger")
        except Exception as e:
            flash(f"Error inesperado al crear estudiante: {e}", "danger")

    return render_template("nuevo_estudiante.html")



@app.route("/estudiantes/<int:id>", methods=["GET"])
def ver_estudiante(id):
    if 'token' not in session:
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("login"))

    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{API_URL_BASE}/estudiantes/{id}", headers=headers)

    if response.status_code == 200:
        try:
            estudiante = response.json()
            return render_template("ver_estudiante.html", estudiante=estudiante)
        except json.JSONDecodeError:
            flash("Error al procesar la información del estudiante recibida de la API.", "danger")
            return redirect(url_for("estudiantes"))
    else:
        try:
            api_data = response.json()
            flash(api_data.get("message", f"No se pudo cargar la información del estudiante (Código: {response.status_code})."), "danger")
        except json.JSONDecodeError:
             flash(f"No se pudo cargar la información del estudiante (Código: {response.status_code}, respuesta no JSON).", "danger")

        return redirect(url_for("estudiantes"))



@app.route("/estudiantes/<int:id>/editar", methods=["GET", "POST"])
def editar_estudiante(id):
    if 'token' not in session:
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("login"))

    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}

    if request.method == "POST":
        data = {
            "nombre": request.form.get("nombre"),
            "apellido": request.form.get("apellido"),
            "edad": request.form.get("edad"),
        }
        response = requests.put(f"{API_URL_BASE}/estudiantes/{id}", headers=headers, json=data)

        if response.status_code == 200:
            flash("Estudiante actualizado con éxito.", "success")
            return redirect(url_for("estudiantes"))
        else:
            try:
                api_data = response.json()
                flash(api_data.get("message", f"Error al actualizar el estudiante (Código: {response.status_code})."), "danger")
            except json.JSONDecodeError:
                flash(f"Error al actualizar el estudiante (Código: {response.status_code}, respuesta no JSON).", "danger")


    response = requests.get(f"{API_URL_BASE}/estudiantes/{id}", headers=headers)
    if response.status_code == 200:
        try:
            estudiante = response.json()
            return render_template("editar_estudiante.html", estudiante=estudiante)
        except json.JSONDecodeError:
            flash("Error al procesar la información del estudiante para editar.", "danger")
            return redirect(url_for("estudiantes"))
    else:
         try:
            api_data = response.json()
            flash(api_data.get("message", f"No se pudo cargar la información del estudiante para editar (Código: {response.status_code})."), "danger")
         except json.JSONDecodeError:
            flash(f"No se pudo cargar la información del estudiante para editar (Código: {response.status_code}, respuesta no JSON).", "danger")

         return redirect(url_for("estudiantes"))



@app.route("/estudiantes/<int:id>/eliminar", methods=["POST"])
def eliminar_estudiante(id):
    if 'token' not in session:
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("login"))

    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.delete(f"{API_URL_BASE}/estudiantes/{id}", headers=headers)

    if response.status_code == 200:
        flash("Estudiante eliminado con éxito.", "success")
    else:
        try:
            api_data = response.json()
            flash(api_data.get("message", f"No se pudo eliminar el estudiante (Código: {response.status_code})."), "danger")
        except json.JSONDecodeError:
             flash(f"No se pudo eliminar el estudiante (Código: {response.status_code}, respuesta no JSON).", "danger")

    return redirect(url_for("estudiantes"))


@app.route("/cursos", methods=["GET"])
def cursos():
    """
    Muestra la lista de cursos, obteniéndolos de la API de Laravel.
    Requiere que el usuario esté completamente autenticado.
    """
    if 'token' not in session or 'user' not in session:
        flash("Por favor, inicia sesión para ver los cursos.", "warning")
        return redirect(url_for("login"))

    token = session['token']
    current_user_data = session['user']
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    query_param = request.args.get("q", "").strip()

    api_url_cursos = f"{API_URL_BASE}/cursos"
    if query_param:
        api_url_cursos += f"?nombre={query_param}"

    cursos = []

    try:
        response = requests.get(api_url_cursos, headers=headers)

        if response.status_code == 200:
            cursos = response.json()
        elif response.status_code == 401:
            flash("Su sesión ha expirado. Por favor, inicie sesión nuevamente.", "warning")
            session.pop('token', None)
            session.pop('email_for_2fa', None)
            session.pop('user', None)
            return redirect(url_for("login"))
        else:
            try:
                api_data = response.json()
                flash(api_data.get("message", f"Error al cargar los cursos (Código: {response.status_code})."), "danger")
            except json.JSONDecodeError:
                flash(f"Error al cargar los cursos (Código: {response.status_code}, respuesta no JSON).", "danger")
            return redirect(url_for("home"))

    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión con la API de cursos: {e}", "danger")
        return redirect(url_for("home"))
    except json.JSONDecodeError:
        flash("Error al procesar la lista de cursos recibida de la API.", "danger")
        return redirect(url_for("home"))

    return render_template("cursos.html", cursos=cursos, current_user=current_user_data)


@app.route("/cursos/<int:id>", methods=["GET"])
def ver_curso(id):
    """
    Muestra los detalles de un curso específico en una página dedicada.
    """
    if 'token' not in session:
        flash("Tu sesión ha expirado o no es válida. Por favor, inicia sesión de nuevo.", "warning")
        return redirect(url_for("login"))

    token = session['token']
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(f"{API_URL_BASE}/cursos/{id}", headers=headers)
        response.raise_for_status()

        curso = response.json()
        app.logger.info(f"Curso {id} cargado exitosamente: {curso.get('nombre')}")

        return render_template("ver_curso.html", curso=curso)

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        app.logger.error(f"Error HTTP al cargar curso {id}: {status_code} - {e.response.text}")
        try:
            api_data = e.response.json()
            error_message = api_data.get("message", f"No se pudo cargar la información del curso (Código: {status_code}).")
        except json.JSONDecodeError:
            error_message = f"No se pudo cargar la información del curso (Código: {status_code}, respuesta no JSON)."

        flash(error_message, "danger")
        return redirect(url_for("cursos"))

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error de conexión con la API al intentar ver el curso {id}: {e}")
        flash(f"Error de conexión con la API al intentar ver el curso: {e}", "danger")
        return redirect(url_for("cursos"))

    except json.JSONDecodeError:
        app.logger.error(f"Error al procesar la información JSON del curso {id} recibida de la API.")
        flash("Error al procesar la información del curso recibida de la API.", "danger")
        return redirect(url_for("cursos"))


@app.route("/cursos/nuevo", methods=["GET", "POST"])
def nuevo_curso():
    """
    Maneja la creación de un nuevo curso (solo para tutores/admins).
    Ahora maneja tanto formularios tradicionales como peticiones AJAX del modal.
    """
    if 'token' not in session or 'user' not in session:
        if request.is_json:
            return jsonify({"success": False, "message": "Por favor, inicia sesión para acceder a esta página."}), 401
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("login"))

    token = session['token']
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    current_user_data = session['user']
    if not has_role_helper(current_user_data, 'tutor') and not has_role_helper(current_user_data, 'administrador'):
        if request.is_json:
            return jsonify({"success": False, "message": "No tienes permiso para crear cursos."}), 403
        flash("No tienes permiso para crear cursos.", "danger")
        return redirect(url_for("cursos"))

    if request.method == "POST":
        if request.is_json:
            data = request.json
            nombre = data.get("nombre")
            descripcion = data.get("descripcion")
            monto = data.get("monto")
            frecuencia = data.get("frecuencia")
            imagen_url = data.get("imagen_url")
            app.logger.debug(f"Datos JSON recibidos para nuevo curso: {data}")
        else:
            nombre = request.form.get("nombre")
            descripcion = request.form.get("descripcion")
            monto = request.form.get("monto")
            frecuencia = request.form.get("frecuencia")
            imagen_url = request.form.get("imagen_url")
            app.logger.debug(f"Datos de formulario recibidos para nuevo curso: {request.form}")

        errors = {}
        if not nombre or not nombre.strip():
            errors['nombre'] = ['El nombre del curso es obligatorio']
        try:
            monto_float = float(monto)
            if monto_float <= 0:
                errors['monto'] = ['El monto debe ser mayor a 0']
        except (ValueError, TypeError):
            errors['monto'] = ['El monto debe ser un número válido']

        if imagen_url and not is_valid_url(imagen_url):
            errors['imagen_url'] = ['URL de imagen no válida']

        if errors:
            app.logger.warning(f"Errores de validación al crear curso: {errors}")
            if request.is_json:
                return jsonify({"success": False, "errors": errors}), 400
            for field, msgs in errors.items():
                for msg in msgs:
                    flash(msg, "danger")
            return render_template("nuevo_curso.html", course_data=request.form, errors=errors)

        payload = {
            "nombre": nombre.strip(),
            "descripcion": descripcion.strip() if descripcion else None,
            "monto": monto_float,
            "frecuencia": frecuencia if frecuencia else None,
            "imagen_url": imagen_url if imagen_url else None,
            "user_id": current_user_data.get('id')
        }

        headers["Content-Type"] = "application/json"

        try:
            app.logger.info(f"Enviando POST a {API_URL_BASE}/cursos con payload: {json.dumps(payload)}")
            response = requests.post(f"{API_URL_BASE}/cursos", headers=headers, json=payload)
            response.raise_for_status()

            if request.is_json:
                app.logger.info("Curso creado con éxito (AJAX).")
                return jsonify({
                    "success": True,
                    "message": "Curso creado con éxito.",
                    "redirect": url_for("cursos")
                }), 200

            flash("Curso creado con éxito.", "success")
            return redirect(url_for("cursos"))

        except requests.exceptions.HTTPError as e:
            error_data = {}
            try:
                error_data = e.response.json()
            except json.JSONDecodeError:
                error_data = {"message": f"Error al crear el curso (Código: {e.response.status_code})"}

            app.logger.error(f"Error HTTP al crear curso: {e.response.status_code} - {error_data.get('message', 'No JSON')}")

            if request.is_json:
                return jsonify({
                    "success": False,
                    "message": error_data.get("message", f"Error al crear el curso (Código: {e.response.status_code})."),
                    "errors": error_data.get('errors', {})
                }), e.response.status_code

            flash(error_data.get("message", f"Error al crear el curso (Código: {e.response.status_code})."), "danger")
            return render_template("nuevo_curso.html", course_data=payload, errors=error_data.get('errors'))

        except requests.exceptions.RequestException as e:
            error_message = f"Error de conexión con la API al crear el curso: {e}"
            app.logger.error(error_message)
            if request.is_json:
                return jsonify({"success": False, "message": error_message}), 500
            flash(error_message, "danger")
            return render_template("nuevo_curso.html", course_data=payload)
        except Exception as e:
            error_message = f"Error inesperado: {e}"
            app.logger.critical(f"Error inesperado en nuevo_curso: {e}", exc_info=True)
            if request.is_json:
                return jsonify({"success": False, "message": error_message}), 500
            flash(error_message, "danger")
            return render_template("nuevo_curso.html", course_data=payload)

    return render_template("nuevo_curso.html")


@app.route("/cursos/<int:id>/editar", methods=["GET", "POST"])
def editar_curso(id):
    app.logger.info(f"--- INICIO DE PROCESAMIENTO DE EDITAR CURSO (ID: {id}) ---")

    if 'token' not in session or 'user' not in session:
        app.logger.warning("Usuario no autenticado para editar curso.")
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "message": "Debes iniciar sesión para editar el curso."}), 401
        flash("Debes iniciar sesión para editar el curso.", "warning")
        return redirect(url_for("login"))

    token = session['token']
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    current_user = session['user']
    app.logger.info(f"Usuario autenticado: {current_user.get('name')} (ID: {current_user.get('id')})")

    curso_data = None
    try:
        app.logger.info(f"Obteniendo detalles del curso {id} de la API...")
        response = requests.get(f"{API_URL_BASE}/cursos/{id}", headers=headers, timeout=10)
        response.raise_for_status()
        curso_data = response.json()
        app.logger.debug(f"Curso obtenido de la API: {curso_data}")

        if not (
            has_role_helper(current_user, 'administrador') or
            (has_role_helper(current_user, 'tutor') and current_user.get("id") == curso_data.get("user_id"))
        ):
            app.logger.warning(f"Acceso denegado. Usuario ID {current_user.get('id')} no es propietario ni admin del curso {id}.")
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"success": False, "message": "No tienes permiso para editar este curso."}), 403
            flash("No tienes permiso para editar este curso.", "danger")
            return redirect(url_for("cursos"))

    except requests.exceptions.HTTPError as e:
        error_message = "Curso no encontrado." if e.response.status_code == 404 else f"Error al obtener el curso: {e}"
        app.logger.error(f"HTTPError al obtener curso: {e.response.status_code} - {e.response.text}")
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "message": error_message}), e.response.status_code
        flash(error_message, "danger")
        return redirect(url_for("cursos"))
    except requests.exceptions.RequestException as e:
        error_message = f"Error de conexión al obtener curso: {e}"
        app.logger.error(f"RequestException al obtener curso: {error_message}")
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "message": error_message}), 500
        flash(error_message, "danger")
        return redirect(url_for("cursos"))

    # Manejar GET request (normalmente para cargar la página de edición, pero aquí redirige si no es AJAX)
    if request.method == "GET":
        app.logger.info("Petición GET. Redirigiendo a /cursos (se espera edición vía AJAX/modal).")
        # Si se desea que se pueda acceder a una página de edición dedicada, aquí se renderizaría:
        # return render_template("editar_curso.html", curso=curso_data)
        return redirect(url_for("cursos"))

    # Manejar POST request (envío del formulario de edición)
    if request.method == "POST":
        app.logger.info("Petición POST recibida para editar curso.")
        data = {}
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                data = request.get_json(force=True)
                app.logger.debug(f"Datos JSON recibidos: {data}")
            except Exception as e:
                app.logger.error(f"Falló al parsear JSON de la solicitud: {e}")
                return jsonify({"success": False, "message": "Error al procesar los datos JSON enviados."}), 400
        else:
            app.logger.warning("Solicitud NO es JSON. Procesando form data (esto no debería ocurrir con el frontend actual).")
            data = {
                "nombre": request.form.get("nombre"),
                "descripcion": request.form.get("descripcion"),
                "monto": request.form.get("monto"),
                "frecuencia": request.form.get("frecuencia"),
                "imagen_url": request.form.get("imagen_url")
            }

        nombre = data.get("nombre")
        descripcion = data.get("descripcion")
        monto = data.get("monto")
        frecuencia = data.get("frecuencia")
        imagen_url = data.get("imagen_url")

        app.logger.debug(f"Datos extraídos (antes de normalizar): nombre={nombre}, monto={monto}, imagen_url={imagen_url}")

        errors = {}

        if not isinstance(nombre, str):
            errors["nombre"] = ["El nombre del curso debe ser una cadena de texto."]
        elif not nombre.strip():
            errors["nombre"] = ["El nombre del curso es obligatorio."]
        else:
            nombre = nombre.strip()

        if monto is None or (isinstance(monto, str) and not str(monto).strip()):
            errors["monto"] = ["El monto es obligatorio."]
        else:
            try:
                monto = float(monto)
                if monto < 0:
                    errors["monto"] = ["El monto debe ser un número positivo."]
            except (ValueError, TypeError):
                errors["monto"] = ["El monto debe ser un número válido."]

        descripcion = descripcion.strip() if isinstance(descripcion, str) and descripcion.strip() else None
        frecuencia = frecuencia.strip() if isinstance(frecuencia, str) and frecuencia.strip() else None
        imagen_url = imagen_url.strip() if isinstance(imagen_url, str) and imagen_url.strip() else None

        if imagen_url and not is_valid_url(imagen_url):
            errors['imagen_url'] = ['URL de imagen no válida.']

        if errors:
            app.logger.warning(f"Errores de validación en el servidor Flask al editar curso: {errors}")
            is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return jsonify({
                    "success": False,
                    "message": "Error de validación.",
                    "errors": errors
                }), 400
            for field, msgs in errors.items():
                for msg in msgs:
                    flash(msg, "danger")
            return redirect(url_for("cursos")) # Redirige a cursos y muestra flashes

        payload = {
            "nombre": nombre,
            "descripcion": descripcion,
            "monto": monto,
            "frecuencia": frecuencia,
            "imagen_url": imagen_url
        }
        app.logger.debug(f"Payload final preparado para la API de Laravel: {payload}")

        api_headers = headers.copy()
        api_headers["Content-Type"] = "application/json"

        try:
            app.logger.info(f"Enviando PUT a {API_URL_BASE}/cursos/{id} con payload: {json.dumps(payload)}")
            put_response = requests.put(
                f"{API_URL_BASE}/cursos/{id}",
                headers=api_headers,
                json=payload,
                timeout=30
            )

            app.logger.info(f"API Response Status (PUT): {put_response.status_code}")
            app.logger.debug(f"API Response Text (PUT): {put_response.text}")

            put_response.raise_for_status()

            is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return jsonify({
                    "success": True,
                    "message": "Curso actualizado correctamente."
                }), 200
            else:
                flash("Curso actualizado correctamente.", "success")
                return redirect(url_for("cursos"))

        except requests.exceptions.HTTPError as e:
            error_data = {"message": "Error al actualizar el curso.", "errors": {}}
            app.logger.error(f"HTTPError de la API (Status: {e.response.status_code}) - {e.response.text}")

            try:
                if e.response.headers.get('content-type', '').startswith('application/json'):
                    error_data = e.response.json()
            except ValueError:
                error_data["message"] = f"Error del servidor (HTTP {e.response.status_code}): {e.response.text}"

            is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return jsonify({
                    "success": False,
                    "message": error_data.get("message", "Error al actualizar el curso."),
                    "errors": error_data.get("errors", {})
                }), e.response.status_code
            else:
                flash(error_data.get("message", "Error al actualizar el curso."), "danger")
                return redirect(url_for("cursos"))

        except requests.exceptions.Timeout:
            error_message = "Tiempo de espera agotado al conectar con la API."
            app.logger.error(f"Timeout: {error_message}")
            is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return jsonify({"success": False, "message": error_message}), 500
            else:
                flash(error_message, "danger")
                return redirect(url_for("cursos"))

        except requests.exceptions.RequestException as e:
            error_message = f"Error de conexión con la API: {str(e)}"
            app.logger.error(f"RequestException: {error_message}")
            is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return jsonify({"success": False, "message": error_message}), 500
            else:
                flash(error_message, "danger")
                return redirect(url_for("cursos"))

    app.logger.warning("Método no permitido o error inesperado al final de la función editar_curso.")
    is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        return jsonify({"success": False, "message": "Método no permitido."}), 405
    else:
        flash("Método no permitido.", "danger")
        return redirect(url_for("cursos"))

# --- NUEVA RUTA: Editar Detalles Adicionales del Curso ---
@app.route('/cursos/<int:curso_id>/editar_detalles', methods=['POST'])
def editar_detalles_curso(curso_id):
    """
    Maneja la solicitud para actualizar los detalles adicionales de un curso
    (días de tutoría, forma de pago, otros).
    Solo accesible para el tutor propietario del curso o un administrador.
    """
    app.logger.info(f"Intento de editar detalles del curso {curso_id}.")

    if 'token' not in session:
        app.logger.warning("Intento de editar detalles del curso sin token en la sesión. Redirigiendo a login.")
        flash("Tu sesión ha expirado o no es válida. Por favor, inicia sesión de nuevo.", "warning")
        return redirect(url_for("login"))

    token = session['token']
    app.logger.info(f"Token de sesión encontrado para el usuario.")

    data = request.get_json()
    app.logger.debug(f"Payload recibido para editar detalles del curso {curso_id}: {data}")

    payload = {
        'dias_tutoria': data.get('dias_tutoria') if data.get('dias_tutoria') else None,
        'forma_pago': data.get('forma_pago') if data.get('forma_pago') else None,
        'otros': data.get('otros') if data.get('otros') else None,
    }

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        app.logger.info(f"Enviando actualización de detalles del curso {curso_id} a Laravel con token.")
        api_response = requests.put(f'{API_URL_BASE}/cursos/{curso_id}', json=payload, headers=headers)
        api_response.raise_for_status()

        app.logger.info(f"Detalles del curso {curso_id} actualizados exitosamente en Laravel.")
        return jsonify({'success': True, 'message': 'Detalles del curso actualizados correctamente.'})

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        app.logger.error(f"Error HTTP de la API al actualizar detalles del curso {curso_id}: {status_code} - {e.response.text}")
        try:
            error_data = e.response.json()
            if status_code == 401 or status_code == 403:
                flash("Tu sesión ha expirado o no es válida. Por favor, inicia sesión de nuevo.", "warning")
                session.pop('token', None)
                return jsonify({'success': False, 'message': 'Sesión inválida. Redirigiendo a login.'}), 401
            return jsonify({'success': False, 'message': error_data.get('message', 'Error al actualizar detalles del curso.'), 'errors': error_data.get('errors', {})}), status_code
        except json.JSONDecodeError:
            return jsonify({'success': False, 'message': f"Error desconocido al actualizar detalles del curso: {e.response.text}"}), status_code
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error de conexión al actualizar detalles del curso {curso_id}: {e}")
        return jsonify({'success': False, 'message': 'Error de conexión con el servidor de la API.'}), 500
    except Exception as e:
        app.logger.error(f"Error inesperado al editar detalles del curso {curso_id}: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'Ocurrió un error inesperado al guardar los detalles.'}), 500


@app.route("/cursos/<int:id>/eliminar", methods=["POST"])
def eliminar_curso(id):
    """
    Maneja la eliminación de un curso (solo para el tutor que lo publicó o admin).
    Retorna una respuesta JSON para solicitudes AJAX del modal.
    """
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    app.logger.info(f"Solicitud de eliminación para curso {id}. Es AJAX: {is_ajax}")

    if 'token' not in session or 'user' not in session:
        message = "Por favor, inicia sesión para acceder a esta página."
        app.logger.warning(f"Intento de eliminar curso {id} sin autenticación. Es AJAX: {is_ajax}")
        if is_ajax:
            return jsonify({'success': False, 'message': message}), 401
        flash(message, "warning")
        return redirect(url_for("login"))

    token = session['token']
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    current_user_data = session['user']

    try:
        app.logger.info(f"Verificando permisos para eliminar curso {id} para usuario {current_user_data.get('id')}.")
        curso_response = requests.get(f"{API_URL_BASE}/cursos/{id}", headers=headers)
        curso_response.raise_for_status()

        curso_data = curso_response.json()

        user_has_admin_role = has_role_helper(current_user_data, 'administrador')
        user_is_tutor_and_owner = (
            has_role_helper(current_user_data, 'tutor') and
            current_user_data.get('id') == curso_data.get('user_id')
        )

        if not (user_has_admin_role or user_is_tutor_and_owner):
            message = "No tienes permiso para eliminar este curso."
            app.logger.warning(f"Usuario {current_user_data.get('id')} sin permiso para eliminar curso {id}.")
            if is_ajax:
                return jsonify({'success': False, 'message': message}), 403
            flash(message, "danger")
            return redirect(url_for("cursos"))

        app.logger.info(f"Permisos verificados para eliminar curso {id}.")

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_message = f"No se pudo cargar el curso para verificar permisos de eliminación (Código: {status_code})."
        try:
            api_data = e.response.json()
            error_message = api_data.get("message", error_message)
        except json.JSONDecodeError:
            pass

        app.logger.error(f"Error HTTP al verificar permisos para eliminar curso {id}: {status_code} - {e.response.text}")
        if is_ajax:
            return jsonify({'success': False, 'message': error_message}), status_code
        flash(error_message, "danger")
        return redirect(url_for("cursos"))
    except requests.exceptions.RequestException as e:
        message = f"Error de conexión con la API al verificar permisos de eliminación: {e}"
        app.logger.error(f"Error de conexión al verificar permisos para eliminar curso {id}: {e}")
        if is_ajax:
            return jsonify({'success': False, 'message': message}), 500
        flash(message, "danger")
        return redirect(url_for("cursos"))
    except json.JSONDecodeError:
        message = f"Error al procesar la respuesta de la API al verificar permisos de eliminación."
        app.logger.error(f"Error JSON al verificar permisos para eliminar curso {id}.")
        if is_ajax:
            return jsonify({'success': False, 'message': message}), 500
        flash(message, "danger")
        return redirect(url_for("cursos"))

    try:
        app.logger.info(f"Enviando solicitud DELETE a la API para curso {id}.")
        response = requests.delete(f"{API_URL_BASE}/cursos/{id}", headers=headers)
        response.raise_for_status()

        message = "Curso eliminado con éxito."
        app.logger.info(f"Curso {id} eliminado exitosamente.")
        if is_ajax:
            return jsonify({'success': True, 'message': message})
        flash(message, "success")
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_message = f"No se pudo eliminar el curso (Código: {status_code})."
        try:
            api_data = e.response.json()
            error_message = api_data.get("message", error_message)
        except json.JSONDecodeError:
            pass

        app.logger.error(f"Error HTTP al eliminar curso {id}: {status_code} - {e.response.text}")
        if is_ajax:
            return jsonify({'success': False, 'message': error_message}), status_code
        flash(error_message, "danger")
    except requests.exceptions.RequestException as e:
        message = f"Error de conexión con la API al eliminar el curso: {e}"
        app.logger.error(f"Error de conexión al eliminar curso {id}: {e}")
        if is_ajax:
            return jsonify({'success': False, 'message': message}), 500
        flash(message, "danger")
    except json.JSONDecodeError:
        message = f"Error al procesar la respuesta de la API al eliminar el curso."
        app.logger.error(f"Error JSON al eliminar curso {id}.")
        if is_ajax:
            return jsonify({'success': False, 'message': message}), 500
        flash(message, "danger")

    if not is_ajax:
        return redirect(url_for("cursos"))


@app.route("/cursos/<int:curso_id>/registrarse", methods=["POST"])
def registrarse_curso(curso_id):
    """
    Permite a un estudiante registrarse en un curso.
    """
    if 'token' not in session or 'user' not in session:
        flash("Por favor, inicia sesión para registrarte en un curso.", "warning")
        return redirect(url_for("login"))

    token = session['token']
    current_user_data = session['user']
    student_id = current_user_data.get('id')

    if not student_id:
        flash("No se pudo obtener el ID del estudiante para registrarse al curso.", "danger")
        return redirect(url_for("cursos"))

    if not has_role_helper(current_user_data, 'estudiante'):
        flash("Solo los estudiantes pueden registrarse en cursos.", "danger")
        return redirect(url_for("cursos"))

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {"curso_id": curso_id}

    try:
        response = requests.post(f"{API_URL_BASE}/estudiantes/{student_id}/asignar-curso", headers=headers, json=data)

        if response.status_code == 200:
            flash("¡Registrado al curso exitosamente!", "success")
        elif response.status_code == 409:
            flash("Ya estás registrado en este curso.", "info")
        else:
            api_data = response.json()
            flash(api_data.get("message", f"Error al registrarse al curso (Código: {response.status_code})."), "danger")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión con la API al registrarse al curso: {e}", "danger")
    except json.JSONDecodeError:
        flash(f"Error al procesar la respuesta de la API al registrarse al curso (Código: {response.status_code}).", "danger")

    return redirect(url_for("cursos"))


@app.route("/logout")
def logout():
    if 'token' in session:
        token = session['token']
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        try:
            requests.post(f"{API_URL}/logout", headers=headers)
            app.logger.info("Token invalidado en la API de Laravel.")
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Error al intentar cerrar sesión en la API de Laravel: {e}")
            pass

    # Limpiar todas las variables de sesión relevantes en Flask
    session.pop('token', None)
    session.pop('email_for_2fa', None)
    session.pop('user', None)
    # Las siguientes se asumen no utilizadas o redundantes y se eliminan
    # session.pop('usuario', None)
    # session.pop('user_name', None)

    flash("Sesión cerrada con éxito.", "info")
    return redirect(url_for("login"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if 'token' in session and 'user' in session:
        # Obtener el email o nombre del usuario del objeto 'user' en sesión
        user_data = session['user']
        display_name = user_data.get('name', user_data.get('email', 'Usuario'))

        if request.method == "POST":
            flash("Funcionalidad de actualización de perfil no implementada completamente.", "info") # Usar "info"
            return redirect(url_for("profile"))

        return render_template("profile.html", user=user_data, display_name=display_name)
    else:
        flash("Por favor, inicia sesión.", "warning")
        return redirect(url_for("login"))


# --- Gestión de usuarios (solo admin) ---
@app.route("/usuarios", methods=["GET"])
def usuarios():
    if 'token' not in session or 'user' not in session:
        flash("Debes iniciar sesión como administrador para acceder a la gestión de usuarios.", "danger")
        return redirect(url_for("login"))
    current_user = session['user']
    if not has_role_helper(current_user, 'administrador'):
        flash("Acceso denegado: solo administradores.", "danger")
        return redirect(url_for("cursos"))

    headers = {"Authorization": f"Bearer {session['token']}", "Accept": "application/json"}
    try:
        response = requests.get(f"{API_URL_BASE}/users", headers=headers)
        if response.status_code == 200:
            usuarios = response.json()
            app.logger.info("Usuarios cargados exitosamente.")
            return render_template("usuarios.html", usuarios=usuarios)
        else:
            api_data = response.json()
            flash(f"Error al obtener usuarios: {api_data.get('message', 'Error desconocido')} (Código: {response.status_code})", "danger")
            app.logger.error(f"Error al obtener usuarios: {response.status_code} - {response.text}")
            return render_template("usuarios.html", usuarios=[])
    except Exception as e:
        flash(f"Error de conexión con la API: {e}", "danger")
        app.logger.error(f"Error de conexión al cargar usuarios: {e}", exc_info=True)
        return render_template("usuarios.html", usuarios=[])

@app.route("/usuarios/nuevo", methods=["GET", "POST"])
def nuevo_usuario():
    if 'token' not in session or 'user' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({"success": False, "message": "Debes iniciar sesión para crear usuarios."}), 401
        flash("Debes iniciar sesión como administrador.", "danger")
        return redirect(url_for("login"))

    current_user = session['user']
    # ⚠️ CORREGIDO: antes era g.has_role
    if not has_role_helper(current_user, 'administrador'):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({"success": False, "message": "Acceso denegado: solo administradores."}), 403
        flash("Acceso denegado: solo administradores.", "danger")
        return redirect(url_for("cursos"))


    if request.method == "POST":
        headers = {"Authorization": f"Bearer {session['token']}", "Accept": "application/json", "Content-Type": "application/json"}
        
        data_to_send = {}
        # Determine if the request is JSON (from AJAX) or form-data (traditional)
        if request.is_json:
            data_to_send = request.get_json()
            app.logger.debug(f"Datos recibidos via JSON para nuevo usuario: {data_to_send}")
        else:
            # This block handles traditional form submissions.
            # Your current frontend uses AJAX, so this might not be hit.
            # Ensure all fields are correctly extracted from request.form
            data_to_send = {
                "name": request.form.get("name"),
                "last_name": request.form.get("last_name"),
                "number": request.form.get("number"),
                "email": request.form.get("email"),
                "password": request.form.get("password"),
                "password_confirmation": request.form.get("password_confirmation"), # Crucial: Add this field
                "role_names": request.form.getlist("roles")
            }
            app.logger.debug(f"Datos recibidos via form-data para nuevo usuario: {data_to_send}")

        try:
            # Ensure 'role_names' is always a list, even if it came from JSON directly
            # This block ensures that 'role_names' is correctly set from 'roles' if present in JSON
            if 'role_names' not in data_to_send and 'roles' in data_to_send:
                data_to_send['role_names'] = data_to_send['roles']
                del data_to_send['roles']
            elif 'role_names' not in data_to_send:
                data_to_send['role_names'] = [] # Ensure it's an empty list if no roles are selected

            app.logger.info(f"Enviando POST a {API_URL_BASE}/users con payload: {json.dumps(data_to_send)}")
            response = requests.post(f"{API_URL_BASE}/users", headers=headers, json=data_to_send)
            
            # Check for successful response (201 Created)
            if response.status_code == 201:
                message = "Usuario creado exitosamente."
                app.logger.info(message)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
                    return jsonify({"success": True, "message": message})
                flash(message, "success")
                return redirect(url_for("usuarios"))
            else:
                # Handle API errors (e.g., 422 Validation Errors, 400 Bad Request, etc.)
                error_data = {}
                try:
                    error_data = response.json()
                except json.JSONDecodeError:
                    app.logger.error(f"API response not JSON: {response.text}")
                    error_data['message'] = f"Error desconocido del servidor (Código: {response.status_code})"

                message = error_data.get('message', 'Error desconocido al crear usuario.')
                app.logger.error(f"Error al crear usuario (Código: {response.status_code}): {response.text}")

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
                    return jsonify({"success": False, "message": message, "errors": error_data.get('errors', {})}), response.status_code
                
                flash(message, "danger")
                # For traditional form submission, re-render with data and errors
                # This part is mostly for non-AJAX, but it's good to have as a fallback
                return render_template("nuevo_usuario.html", data=data_to_send, error=error_data)

        except requests.exceptions.RequestException as e:
            message = f"Error de conexión con la API: {e}"
            app.logger.error(f"Error de conexión al crear usuario: {e}", exc_info=True)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
                return jsonify({"success": False, "message": message}), 500
            flash(message, "danger")
            return render_template("nuevo_usuario.html", data=data_to_send)
        except Exception as e:
            message = f"Error inesperado: {e}"
            app.logger.error(f"Error inesperado al crear usuario: {e}", exc_info=True)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
                return jsonify({"success": False, "message": message}), 500
            flash(message, "danger")
            return render_template("nuevo_usuario.html", data=data_to_send)

    # For GET request, simply render the form
    return render_template("nuevo_usuario.html")

@app.route("/usuarios/<int:id>", methods=["GET"])
def ver_usuario(id):
    if 'token' not in session or 'user' not in session:
        flash("Debes iniciar sesión como administrador.", "danger")
        return redirect(url_for("login"))
    current_user = session['user']
    if not has_role_helper(current_user, 'administrador'):
        flash("Acceso denegado: solo administradores.", "danger")
        return redirect(url_for("cursos"))

    headers = {"Authorization": f"Bearer {session['token']}", "Accept": "application/json"}
    try:
        response = requests.get(f"{API_URL_BASE}/users/{id}", headers=headers)
        if response.status_code == 200:
            usuario = response.json()
            app.logger.info(f"Usuario {id} cargado exitosamente.")
            return render_template("ver_usuario.html", usuario=usuario)
        else:
            flash("Usuario no encontrado.", "danger")
            app.logger.warning(f"Usuario {id} no encontrado (Código: {response.status_code}).")
            return redirect(url_for("usuarios"))
    except Exception as e:
        flash(f"Error de conexión: {e}", "danger")
        app.logger.error(f"Error de conexión al ver usuario {id}: {e}", exc_info=True)
        return redirect(url_for("usuarios"))

@app.route("/usuarios/<int:id>/editar", methods=["GET", "POST"])
def editar_usuario(id):
    if 'token' not in session or 'user' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "message": "Debes iniciar sesión como administrador."}), 401
        flash("Debes iniciar sesión como administrador.", "danger")
        return redirect(url_for("login"))

    current_user = session['user']
    if not has_role_helper(current_user, 'administrador'):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "message": "Acceso denegado: solo administradores."}), 403
        flash("Acceso denegado: solo administradores.", "danger")
        return redirect(url_for("cursos"))

    headers = {"Authorization": f"Bearer {session['token']}", "Accept": "application/json"}

    if request.method == "POST":
        headers["Content-Type"] = "application/json"

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = request.get_json()
            app.logger.debug(f"Datos recibidos via AJAX para editar usuario {id}: {data}")
        else:
            data = {
                "name": request.form.get("name"),
                "last_name": request.form.get("last_name"),
                "number": request.form.get("number"),
                "email": request.form.get("email"),
                "role_names": request.form.getlist("roles")
            }
            password = request.form.get("password")
            if password:
                data["password"] = password
            app.logger.debug(f"Datos de formulario recibidos para editar usuario {id}: {data}")

        try:
            response = requests.put(f"{API_URL_BASE}/users/{id}", headers=headers, json=data)
            if response.status_code == 200:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    app.logger.info(f"Usuario {id} actualizado exitosamente via AJAX.")
                    return jsonify({"success": True, "message": "Usuario actualizado exitosamente."})
                flash("Usuario actualizado exitosamente.", "success")
                app.logger.info(f"Usuario {id} actualizado exitosamente.")
                return redirect(url_for("usuarios"))
            else:
                error_data = response.json()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    app.logger.error(f"Error AJAX al actualizar usuario {id} (Código: {response.status_code}): {response.text}")
                    return jsonify({"success": False, "message": error_data.get('message', 'Error desconocido'), "errors": error_data.get('errors', {})}), response.status_code
                flash(f"Error al actualizar usuario: {error_data.get('message', 'Error desconocido')}", "danger")
                app.logger.error(f"Error al actualizar usuario {id} (Código: {response.status_code}): {response.text}")
                user_response = requests.get(f"{API_URL_BASE}/users/{id}", headers=headers)
                if user_response.status_code == 200:
                    usuario = user_response.json()
                    return render_template("editar_usuario.html", usuario=usuario, error=error_data)
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                app.logger.error(f"Error de conexión AJAX al actualizar usuario {id}: {e}", exc_info=True)
                return jsonify({"success": False, "message": f"Error de conexión: {e}"}), 500
            flash(f"Error de conexión: {e}", "danger")
            app.logger.error(f"Error de conexión al actualizar usuario {id}: {e}", exc_info=True)

    try:
        response = requests.get(f"{API_URL_BASE}/users/{id}", headers=headers)
        if response.status_code == 200:
            usuario = response.json()
            app.logger.info(f"Formulario de edición para usuario {id} cargado.")
            return render_template("editar_usuario.html", usuario=usuario)
        else:
            flash("Usuario no encontrado.", "danger")
            app.logger.warning(f"Usuario {id} no encontrado para edición (Código: {response.status_code}).")
            return redirect(url_for("usuarios"))
    except Exception as e:
        flash(f"Error de conexión: {e}", "danger")
        app.logger.error(f"Error de conexión al cargar formulario de edición para usuario {id}: {e}", exc_info=True)
        return redirect(url_for("usuarios"))

@app.route("/usuarios/<int:id>/eliminar", methods=["POST"])
def eliminar_usuario(id):
    if 'token' not in session or 'user' not in session:
        flash("Debes iniciar sesión como administrador.", "danger")
        return redirect(url_for("login"))
    current_user = session['user']
    if not has_role_helper(current_user, 'administrador'):
        flash("Acceso denegado: solo administradores.", "danger")
        return redirect(url_for("cursos"))

    headers = {"Authorization": f"Bearer {session['token']}", "Accept": "application/json"}
    try:
        response = requests.delete(f"{API_URL_BASE}/users/{id}", headers=headers)
        if response.status_code == 200:
            flash("Usuario eliminado exitosamente.", "success")
            app.logger.info(f"Usuario {id} eliminado exitosamente.")
        else:
            error_data = response.json()
            flash(f"Error al eliminar usuario: {error_data.get('message', 'Error desconocido')}", "danger")
            app.logger.error(f"Error al eliminar usuario {id} (Código: {response.status_code}): {response.text}")
    except Exception as e:
        flash(f"Error de conexión: {e}", "danger")
        app.logger.error(f"Error de conexión al eliminar usuario {id}: {e}", exc_info=True)

    return redirect(url_for("usuarios"))


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

