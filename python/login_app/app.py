from flask import Flask, render_template, request, redirect, url_for, flash,jsonify, session
import requests
import zeep  
import json 
import re 
import os
from urllib.parse import urlparse # Asegúrate de que esta importación esté al principio de tu app.py
from datetime import datetime # Asegúrate de que esta importación esté al principio de tu app.py
import pytz # Asegúrate de que esta importación esté al principio de tu app.py
app = Flask(__name__)
app.secret_key = 'clave_secreta'  


API_URL = os.environ.get("LARAVEL_API_URL", "http://localhost:8000/api")
API_URL_BASE = os.environ.get("LARAVEL_API_BASE_URL", "http://localhost:8000/api/v1")

#WEB_URL = os.environ.get("LARAVEL_API_BASE_URL", "http://localhost:8000/api/v1") + "/soap"
#WEB_URL_BASE = os.environ.get("LARAVEL_API_BASE_URL", "http://localhost:8000/api/v1") + "/soap_cursos"


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
    return False
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
    
        import re
        match = re.search(r'at least (\d+) characters', message)
        if match:
            min_chars = match.group(1)
            translated_message = translated_message.replace(':min', min_chars)

    if ':attribute' in translated_message and field_name:
        
        translated_field_name = VALIDATION_MESSAGES_ES.get(field_name, field_name)
        translated_message = translated_message.replace(':attribute', translated_field_name)

    return translated_message

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

        # 2.  login con Laravel API
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        payload = {"email": email, "password": password}

        try:
            api_response = requests.post(f"{API_URL}/login", headers=headers, json=payload)
            api_data = api_response.json()

            print("API Response Status Code (Login):", api_response.status_code)
            print("API Response Content (Login):", api_response.text)

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

            print("Verify 2FA API Response Status Code:", api_response.status_code)
            print("Verify 2FA API Response Content:", api_response.text)

            if api_response.status_code == 200:
                # CAMBIO CLAVE: AQUÍ es donde obtenemos el token por primera vez
                token = api_data.get("token")
                user = api_data.get("user")

                if token:
                    # Guardar el token recién obtenido
                    session['token'] = token
                    
                   
                    if user:
                        session['user'] = user
                    else:
                        # Si no, hacer una petición adicional para obtener los datos del usuario
                        user_info_headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
                        user_info_response = requests.get(f"{API_URL}/user", headers=user_info_headers)

                        if user_info_response.status_code == 200:
                            session['user'] = user_info_response.json()
                        else:
                            flash("Error al obtener la información de su perfil después de la verificación 2FA.", "danger")
                            session.clear()  # Limpiar toda la sesión
                            return redirect(url_for("login"))

                    # Limpiar datos temporales del proceso 2FA
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

    # Para GET request o si POST falla y se vuelve a renderizar
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
        # Recoge todos los campos del formulario, incluyendo los nuevos
        name = request.form.get("name") # Cambiado de 'nombre' a 'name'
        last_name = request.form.get("last_name") # Nuevo campo
        number = request.form.get("number") # Nuevo campo
        email = request.form.get("email")
        role = request.form.get("role") # Nuevo campo
        password = request.form.get("password")
        password_confirmation = request.form.get("password_confirmation")
        recaptcha_response = request.form.get("g-recaptcha-response")

        # Verificación de reCAPTCHA
        data = {
            'secret': RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        response = requests.post(verify_url, data=data)
        result = response.json()

        if result.get('success'):
            # Si reCAPTCHA es exitoso, envía los datos a la API de Laravel
            api_response = requests.post(f"{API_URL}/register", json={
                "name": name,
                "last_name": last_name, # Incluye el nuevo campo
                "number": number,       # Incluye el nuevo campo
                "email": email,
                "role": role,           # Incluye el nuevo campo
                "password": password,
                "password_confirmation": password_confirmation
            })

            print("Register API Response Status Code:", api_response.status_code)
            print("Register API Response Content:", api_response.text)

            if api_response.status_code == 201:
                flash("Registro exitoso, por favor inicia sesión.", "success") # Añadido categoría 'success'
                return redirect(url_for("login"))

            elif api_response.status_code == 422:
                try:
                    api_data = api_response.json()
                    error_message = "Errores de validación:"

                    if 'errors' in api_data:
                        for field, messages in api_data['errors'].items():
                            # Traduce el nombre del campo y los mensajes de error
                            translated_messages = [translate_validation_message(msg, field) for msg in messages]
                            error_message += f"\n- {translate_validation_message(field)}: {', '.join(translated_messages)}"
                    else:
                        # Si no hay 'errors' pero es 422, usa el mensaje general
                        error_message = translate_validation_message(api_data.get("message", f"Error de validación desconocido (Código: {api_response.status_code})."))

                    flash(error_message, "error") # Añadido categoría 'error'

                except json.JSONDecodeError:
                    flash(f"Error al procesar errores de validación de la API (Código: 422, respuesta no JSON).", "error") # Añadido categoría 'error'

                return redirect(url_for("register"))

            else:
                try:
                    api_data = api_response.json()
                    error_message = api_data.get("message", f"Error al registrar usuario (Código: {api_response.status_code})")
                    flash(error_message, "error") # Añadido categoría 'error'

                except json.JSONDecodeError:
                    flash(f"Error al procesar la respuesta de registro de la API (Código: {api_response.status_code}).", "error") # Añadido categoría 'error'

                return redirect(url_for("register"))

        else:
            # Error de reCAPTCHA
            flash("Error de CAPTCHA. Por favor, intenta nuevamente.", "error") # Añadido categoría 'error'
            return redirect(url_for("register"))

    # Para solicitudes GET, simplemente renderiza el formulario
    return render_template("register.html", recaptcha_site_key=RECAPTCHA_SITE_KEY)



@app.route("/hola")
def hola():
    
    
    if 'token' in session:
        
        
        flash("Ya has iniciado sesión.")
        return redirect(url_for("estudiantes")) 
    else:
        flash("Por favor, inicia sesión.")
        return redirect(url_for("login"))


@app.route("/estudiantes", methods=["GET"])
def estudiantes():
    
    if 'token' not in session:
        flash("Por favor, inicia sesión.")
        return redirect(url_for("login"))

    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}

    
    query = request.args.get("q", "").strip().lower()

    
    
    response = requests.get(f"{API_URL_BASE}/estudiantes", headers=headers)

    if response.status_code == 200:
        try:
            estudiantes = response.json()
            
            user_name = session.get('user_name', 'Usuario') 
            
            now = datetime.datetime.now() 
            current_date = now.strftime("%d/%m/%Y") 
            current_time = now.strftime("%I:%M:%S %p") 
            
            if query:
                estudiantes = [
                    est for est in estudiantes
                    if query in est.get("nombre", "").lower() or query in est.get("apellido", "").lower() 
                ]
            return render_template("estudiantes.html", estudiantes=estudiantes, user_name=user_name, current_date=current_date, current_time=current_time)
        except json.JSONDecodeError:
            flash("Error al procesar la lista de estudiantes recibida de la API.")
            return redirect(url_for("home")) 


    else:
        
        if response.status_code == 401:
            flash("Su sesión ha expirado. Por favor, inicie sesión nuevamente.")
            
            session.pop('token', None)
            session.pop('email_for_2fa', None) 
            
            return redirect(url_for("login"))
        else:
             
            try:
                api_data = response.json()
                flash(api_data.get("message", f"Error al cargar los estudiantes (Código: {response.status_code})."))
            except json.JSONDecodeError:
                 flash(f"Error al cargar los estudiantes (Código: {response.status_code}, respuesta no JSON).")

            return redirect(url_for("home")) 





@app.route("/estudiantes/nuevo", methods=["GET", "POST"])
def nuevo_estudiante():
    if 'token' not in session:
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("login"))

    token = session['token']
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "text/xml"}

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

        response = requests.post(WEB_URL, headers=headers, data=payload)

        if response.status_code == 200:
            
            
            if "id" in response.text:
                flash("Estudiante creado con éxito.", "success")
                return redirect(url_for("estudiantes"))
            else:
                
                flash("Error al crear el estudiante. Verifica los datos o la respuesta del servicio SOAP.", "danger")
                
                
        else:
            flash(f"Error al conectar con el servicio SOAP. Código de estado: {response.status_code}", "danger")
            
            


    
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
    # Esta es la primera verificación: si no hay token o user, redirigir
    if 'token' not in session or 'user' not in session:
        flash("Por favor, inicia sesión para ver los cursos.", "warning")
        return redirect(url_for("login"))

    token = session['token']
    current_user_data = session['user'] # ¡Obtenemos el usuario de la sesión!
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    # 2. Obtener la lista de cursos
    query_param = request.args.get("q", "").strip() # Obtener el parámetro de búsqueda
    
    api_url_cursos = f"{API_URL_BASE}/cursos"
    if query_param:
        # Tu API Laravel espera 'nombre' para filtrar, si no, se filtra en Flask
        api_url_cursos += f"?nombre={query_param}" 

    cursos = [] # Inicializar cursos como una lista vacía

    try:
        response = requests.get(api_url_cursos, headers=headers)
        
        if response.status_code == 200:
            cursos = response.json()
            # No es necesario filtrar aquí si la API de Laravel ya lo hace por rol/tutor_id
            
        elif response.status_code == 401:
            flash("Su sesión ha expirado. Por favor, inicie sesión nuevamente.", "warning")
            session.pop('token', None)
            session.pop('email_for_2fa', None)
            session.pop('user', None) # Limpiar el usuario también
            return redirect(url_for("login"))
        else:
            try:
                api_data = response.json()
                flash(api_data.get("message", f"Error al cargar los cursos (Código: {response.status_code})."), "danger")
            except json.JSONDecodeError:
                flash(f"Error al cargar los cursos (Código: {response.status_code}, respuesta no JSON).", "danger")
            return redirect(url_for("home")) # Redirigir a home o a una página de error

    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión con la API de cursos: {e}", "danger")
        return redirect(url_for("home")) # Redirigir a home o a una página de error
    except json.JSONDecodeError:
        flash("Error al procesar la lista de cursos recibida de la API.", "danger")
        return redirect(url_for("home")) 

    return render_template("cursos.html", cursos=cursos, current_user=current_user_data)


@app.route("/cursos/<int:id>", methods=["GET"]) 
def ver_curso(id):
    """
    Muestra los detalles de un curso específico en una página dedicada.
    Esta ruta es útil si un usuario accede directamente al curso por URL,
    o si necesitas una vista de detalles más completa que el modal.
    """
    # La autenticación ya se maneja por @login_required.
    # Verificamos la existencia del token API en la sesión.
    if 'token' not in session: # Usando 'token' como lo has solicitado
        flash("Tu sesión ha expirado o no es válida. Por favor, inicia sesión de nuevo.", "warning")
        return redirect(url_for("login"))

    token = session['token'] # Usando 'token' como lo has solicitado
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    try:
        # Realiza la solicitud GET a la API de Laravel para obtener los detalles del curso
        response = requests.get(f"{API_URL_BASE}/cursos/{id}", headers=headers)
        response.raise_for_status() # Lanza un HTTPError para códigos de estado 4xx/5xx

        curso = response.json()
        app.logger.info(f"Curso {id} cargado exitosamente: {curso.get('nombre')}")
        
        # Renderiza el template dedicado para un solo curso, pasando los datos del curso
        return render_template("ver_curso.html", curso=curso)

    except requests.exceptions.HTTPError as e:
        # Manejo de errores HTTP (ej. 404 Not Found, 401 Unauthorized)
        status_code = e.response.status_code
        app.logger.error(f"Error HTTP al cargar curso {id}: {status_code} - {e.response.text}")
        try:
            api_data = e.response.json()
            error_message = api_data.get("message", f"No se pudo cargar la información del curso (Código: {status_code}).")
        except json.JSONDecodeError:
            error_message = f"No se pudo cargar la información del curso (Código: {status_code}, respuesta no JSON)."
        
        flash(error_message, "danger")
        return redirect(url_for("cursos")) # Redirige a la lista de cursos en caso de error

    except requests.exceptions.RequestException as e:
        # Manejo de errores de conexión (ej. API no disponible)
        app.logger.error(f"Error de conexión con la API al intentar ver el curso {id}: {e}")
        flash(f"Error de conexión con la API al intentar ver el curso: {e}", "danger")
        return redirect(url_for("cursos"))

    except json.JSONDecodeError:
        # Manejo de errores si la respuesta de la API no es un JSON válido
        app.logger.error(f"Error al procesar la información JSON del curso {id} recibida de la API.")
        flash("Error al procesar la información del curso recibida de la API.", "danger")
        return redirect(url_for("cursos"))


@app.route("/cursos/nuevo", methods=["GET", "POST"])
def nuevo_curso():
    """
    Maneja la creación de un nuevo curso (solo para tutores/admins).
    Ahora maneja tanto formularios tradicionales como peticiones AJAX del modal.
    """
    # Manejo de autenticación y permisos
    if 'token' not in session or 'user' not in session:
        if request.is_json: # Usar request.is_json para detectar AJAX
            return jsonify({"success": False, "message": "Por favor, inicia sesión para acceder a esta página."}), 401
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("login"))

    token = session['token']
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"} # Content-Type se añade en la llamada a requests.post

    current_user_data = session['user']
    if not has_role_helper(current_user_data, 'tutor') and not has_role_helper(current_user_data, 'administrador'):
        if request.is_json:
            return jsonify({"success": False, "message": "No tienes permiso para crear cursos."}), 403
        flash("No tienes permiso para crear cursos.", "danger")
        return redirect(url_for("cursos"))

    if request.method == "POST":
        # === CAMBIO CLAVE AQUÍ: Usar request.json para JSON y request.form para form-data ===
        if request.is_json:
            data = request.json # Obtener los datos JSON directamente
            nombre = data.get("nombre")
            descripcion = data.get("descripcion")
            monto = data.get("monto")
            frecuencia = data.get("frecuencia")
            imagen_url = data.get("imagen_url")
        else:
            # Fallback para formularios tradicionales (no esperado con el JS actualizado del modal)
            nombre = request.form.get("nombre")
            descripcion = request.form.get("descripcion")
            monto = request.form.get("monto")
            frecuencia = request.form.get("frecuencia")
            imagen_url = request.form.get("imagen_url")

        # Validaciones básicas del lado del servidor
        errors = {}
        if not nombre or not nombre.strip():
            errors['nombre'] = ['El nombre del curso es obligatorio']
        # Asegúrate de que monto sea un número válido y mayor que 0
        try:
            monto_float = float(monto)
            if monto_float <= 0:
                errors['monto'] = ['El monto debe ser mayor a 0']
        except (ValueError, TypeError):
            errors['monto'] = ['El monto debe ser un número válido']
        
        if imagen_url and not is_valid_url(imagen_url):
            errors['imagen_url'] = ['URL de imagen no válida']

        if errors:
            if request.is_json: # Usar request.is_json para la respuesta AJAX
                return jsonify({"success": False, "errors": errors}), 400
            # Para formularios tradicionales, puedes renderizar la plantilla de nuevo con errores
            return render_template("nuevo_curso.html", course_data=request.form, errors=errors)

        payload = {
            "nombre": nombre.strip(),
            "descripcion": descripcion.strip() if descripcion else None, # Enviar None si está vacío
            "monto": monto_float,
            "frecuencia": frecuencia if frecuencia else None, # Enviar None si está vacío
            "imagen_url": imagen_url if imagen_url else None, # Enviar None si está vacío
            "user_id": current_user_data.get('id') # El user_id es crucial para Laravel
            # === ELIMINADOS: "tutor_nombre" y "tutor_apellido" ===
            # Estos campos no son necesarios porque Laravel obtiene el tutor del user_id
        }

        # Asegurarse de que el Content-Type para la API es JSON
        headers["Content-Type"] = "application/json"

        try:
            # Llamar a la API REST de Laravel para crear el curso
            response = requests.post(f"{API_URL_BASE}/cursos", headers=headers, json=payload)
            response.raise_for_status() # Lanza una excepción si la respuesta no es 2xx
            
            # Si todo sale bien
            if request.is_json: # Usar request.is_json para la respuesta AJAX
                return jsonify({
                    "success": True, 
                    "message": "Curso creado con éxito.",
                    "redirect": url_for("cursos") # Puedes enviar la URL de redirección
                }), 200
            
            flash("Curso creado con éxito.", "success")
            return redirect(url_for("cursos"))
                
        except requests.exceptions.HTTPError as e:
            error_data = {}
            try:
                error_data = e.response.json()
            except json.JSONDecodeError:
                error_data = {"message": f"Error al crear el curso (Código: {e.response.status_code})"}
            
            if request.is_json: # Usar request.is_json para la respuesta AJAX
                return jsonify({
                    "success": False,
                    "message": error_data.get("message", f"Error al crear el curso (Código: {e.response.status_code})."),
                    "errors": error_data.get('errors', {})
                }), e.response.status_code
            
            flash(error_data.get("message", f"Error al crear el curso (Código: {e.response.status_code})."), "danger")
            return render_template("nuevo_curso.html", course_data=payload, errors=error_data.get('errors'))
                
        except requests.exceptions.RequestException as e:
            error_message = f"Error de conexión con la API al crear el curso: {e}"
            if request.is_json: # Usar request.is_json para la respuesta AJAX
                return jsonify({"success": False, "message": error_message}), 500
            flash(error_message, "danger")
            return render_template("nuevo_curso.html", course_data=payload) # Pasar payload para mantener datos
        except Exception as e:
            error_message = f"Error inesperado: {e}"
            if request.is_json: # Usar request.is_json para la respuesta AJAX
                return jsonify({"success": False, "message": error_message}), 500
            flash(error_message, "danger")
            return render_template("nuevo_curso.html", course_data=payload) # Pasar payload para mantener datos
        
    # Si es una petición GET, simplemente renderiza el formulario vacío o con datos previos
    return render_template("nuevo_curso.html") # No necesitas pasar course_data o errors aquí para GET inicial


@app.route("/cursos/<int:id>/editar", methods=["GET", "POST"])
def editar_curso(id):
    print(f"\n--- INICIO DE PROCESAMIENTO DE EDITAR CURSO (ID: {id}) ---")

    # Verificar autenticación
    if 'token' not in session or 'user' not in session:
        print("DEBUG: Usuario no autenticado.")
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
    print(f"DEBUG: Usuario autenticado: {current_user.get('name')} (ID: {current_user.get('id')})")

    # Verificar permisos obteniendo el curso
    curso_data = None
    try:
        print(f"DEBUG: Obteniendo detalles del curso {id} de la API...")
        response = requests.get(f"{API_URL_BASE}/cursos/{id}", headers=headers, timeout=10)
        response.raise_for_status()
        curso_data = response.json()
        print(f"DEBUG: Curso obtenido de la API: {curso_data}")
        
        # Verificar permisos
        if not (
            has_role_helper(current_user, 'administrador') or
            (has_role_helper(current_user, 'tutor') and current_user.get("id") == curso_data.get("user_id"))
        ):
            print(f"DEBUG: Acceso denegado. Usuario ID {current_user.get('id')} no es propietario ni admin.")
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"success": False, "message": "No tienes permiso para editar este curso."}), 403
            flash("No tienes permiso para editar este curso.", "danger")
            return redirect(url_for("cursos"))

    except requests.exceptions.HTTPError as e:
        error_message = "Curso no encontrado." if e.response.status_code == 404 else f"Error al obtener el curso: {e}"
        print(f"ERROR: HTTPError al obtener curso: {e.response.status_code} - {e.response.text}")
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "message": error_message}), e.response.status_code
        flash(error_message, "danger")
        return redirect(url_for("cursos"))
    except requests.exceptions.RequestException as e:
        error_message = f"Error de conexión al obtener curso: {e}"
        print(f"ERROR: RequestException al obtener curso: {error_message}")
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "message": error_message}), 500
        flash(error_message, "danger")
        return redirect(url_for("cursos"))

    # Manejar GET request (normalmente para cargar la página de edición, pero aquí redirige)
    if request.method == "GET":
        print("DEBUG: Petición GET. Redirigiendo a /cursos.")
        return redirect(url_for("cursos"))

    # Manejar POST request (envío del formulario de edición)
    if request.method == "POST":
        print("DEBUG: Petición POST recibida.")
        data = {}
        if request.is_json:
            try:
                data = request.get_json(force=True) # force=True para intentar parsear siempre
                print(f"DEBUG: Datos JSON recibidos: {data}")
            except Exception as e:
                print(f"ERROR: Falló al parsear JSON de la solicitud: {e}")
                return jsonify({"success": False, "message": "Error al procesar los datos JSON enviados."}), 400
        else:
            print("DEBUG: Solicitud NO es JSON. Procesando form data (esto no debería ocurrir con el frontend actual).")
            # Fallback para form data (aunque el frontend ahora envía JSON)
            data = {
                "nombre": request.form.get("nombre"),
                "descripcion": request.form.get("descripcion"),
                "monto": request.form.get("monto"),
                "frecuencia": request.form.get("frecuencia"),
                "imagen_url": request.form.get("imagen_url")
            }
        
        # Extraer y normalizar datos
        # Asegurarse de que los valores sean strings o None, y limpiar espacios
        nombre = data.get("nombre")
        descripcion = data.get("descripcion")
        monto = data.get("monto")
        frecuencia = data.get("frecuencia")
        imagen_url = data.get("imagen_url")

        print(f"DEBUG: Datos extraídos (antes de normalizar):")
        print(f"  nombre: {nombre} (Tipo: {type(nombre)})")
        print(f"  descripcion: {descripcion} (Tipo: {type(descripcion)})")
        print(f"  monto: {monto} (Tipo: {type(monto)})")
        print(f"  frecuencia: {frecuencia} (Tipo: {type(frecuencia)})")
        print(f"  imagen_url: {imagen_url} (Tipo: {type(imagen_url)})")

        # Validaciones y normalización de tipos para el payload
        errors = {}
        
        # Validar nombre
        if not isinstance(nombre, str):
            errors["nombre"] = ["El nombre del curso debe ser una cadena de texto."]
        elif not nombre.strip():
            errors["nombre"] = ["El nombre del curso es obligatorio."]
        else:
            nombre = nombre.strip() # Limpiar espacios si es una cadena válida

        # Validar monto
        if monto is None or (isinstance(monto, str) and not monto.strip()):
            errors["monto"] = ["El monto es obligatorio."]
        else:
            try:
                monto = float(monto)
                if monto < 0:
                    errors["monto"] = ["El monto debe ser un número positivo."]
            except (ValueError, TypeError):
                errors["monto"] = ["El monto debe ser un número válido."]

        # Normalizar descripción, frecuencia, imagen_url (a string limpio o None)
        descripcion = descripcion.strip() if isinstance(descripcion, str) and descripcion.strip() else None
        frecuencia = frecuencia.strip() if isinstance(frecuencia, str) and frecuencia.strip() else None
        imagen_url = imagen_url.strip() if isinstance(imagen_url, str) and imagen_url.strip() else None

        # Validar URL de imagen si no es None
        if imagen_url and not is_valid_url(imagen_url):
            errors['imagen_url'] = ['URL de imagen no válida.']

        if errors:
            print(f"DEBUG: Errores de validación en el servidor Flask: {errors}")
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
            return redirect(url_for("cursos"))

        # Preparar payload para la API de Laravel
        payload = {
            "nombre": nombre, # Ya es una cadena limpia o se generó un error
            "descripcion": descripcion, # Ya es una cadena limpia o None
            "monto": monto, # Ya es float o se generó un error
            "frecuencia": frecuencia, # Ya es una cadena limpia o None
            "imagen_url": imagen_url # Ya es una cadena limpia o None
        }
        print(f"DEBUG: Payload final preparado para la API de Laravel: {payload}")
        print(f"DEBUG: Tipo de 'nombre' en payload: {type(payload['nombre'])}")


        api_headers = headers.copy()
        api_headers["Content-Type"] = "application/json"

        try:
            print(f"DEBUG: Enviando PUT a {API_URL_BASE}/cursos/{id} con payload: {json.dumps(payload)}")
            put_response = requests.put(
                f"{API_URL_BASE}/cursos/{id}", 
                headers=api_headers, 
                json=payload,
                timeout=30 
            )
            
            print(f"DEBUG: API Response Status (PUT): {put_response.status_code}")
            print(f"DEBUG: API Response Text (PUT): {put_response.text}")
            
            put_response.raise_for_status() # Lanza HTTPError para 4xx/5xx
            
            # Respuesta exitosa
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
            # Manejar errores HTTP de la API
            error_data = {"message": "Error al actualizar el curso.", "errors": {}}
            print(f"ERROR: HTTPError de la API (Status: {e.response.status_code})")
            
            try:
                if e.response.headers.get('content-type', '').startswith('application/json'):
                    error_data = e.response.json()
                    print(f"ERROR: Datos de error JSON de la API: {error_data}")
            except ValueError:
                error_data["message"] = f"Error del servidor (HTTP {e.response.status_code}): {e.response.text}"
                print(f"ERROR: Datos de error no-JSON de la API: {error_data['message']}")

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
            print(f"ERROR: Timeout: {error_message}")
            is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return jsonify({"success": False, "message": error_message}), 500
            else:
                flash(error_message, "danger")
                return redirect(url_for("cursos"))
                
        except requests.exceptions.RequestException as e:
            error_message = f"Error de conexión con la API: {str(e)}"
            print(f"ERROR: RequestException: {error_message}")
            is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return jsonify({"success": False, "message": error_message}), 500
            else:
                flash(error_message, "danger")
                return redirect(url_for("cursos"))

    # Fallback para métodos no soportados
    print("DEBUG: Método no permitido o error inesperado al final de la función.")
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

    # --- VERIFICACIÓN DE AUTENTICACIÓN BASADA EN SESIÓN ---
    if 'token' not in session:
        app.logger.warning("Intento de editar detalles del curso sin token en la sesión. Redirigiendo a login.")
        flash("Tu sesión ha expirado o no es válida. Por favor, inicia sesión de nuevo.", "warning")
        return redirect(url_for("login"))

    token = session['token']
    app.logger.info(f"Token de sesión encontrado para el usuario.")
    # --- FIN DE VERIFICACIÓN DE AUTENTICACIÓN ---

    # Obtener los datos del formulario JSON
    data = request.get_json()
    app.logger.debug(f"Payload recibido para editar detalles del curso {curso_id}: {data}")

    # Construir el payload para la API de Laravel
    # Asegúrate de que los campos vacíos se envíen como null si tu API Laravel lo espera así
    payload = {
        'dias_tutoria': data.get('dias_tutoria') if data.get('dias_tutoria') else None,
        'forma_pago': data.get('forma_pago') if data.get('forma_pago') else None,
        'otros': data.get('otros') if data.get('otros') else None,
    }
    
    # Configurar los encabezados con el token de autorización
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json' # Es buena práctica incluir Accept
    }

    try:
        # Realizar la solicitud PUT a la API de Laravel para actualizar el curso
        app.logger.info(f"Enviando actualización de detalles del curso {curso_id} a Laravel con token.")
        api_response = requests.put(f'{API_URL_BASE}/cursos/{curso_id}', json=payload, headers=headers)
        api_response.raise_for_status() # Lanza un error para códigos de estado HTTP 4xx/5xx

        app.logger.info(f"Detalles del curso {curso_id} actualizados exitosamente en Laravel.")
        return jsonify({'success': True, 'message': 'Detalles del curso actualizados correctamente.'})

    except requests.exceptions.HTTPError as e:
        # Manejo de errores HTTP de la API de Laravel
        status_code = e.response.status_code
        app.logger.error(f"Error HTTP de la API al actualizar detalles del curso {curso_id}: {status_code} - {e.response.text}")
        try:
            error_data = e.response.json()
            # Si el token es inválido o expiró según la API, redirigir al login
            if status_code == 401 or status_code == 403: # 401 Unauthorized, 403 Forbidden
                flash("Tu sesión ha expirado o no es válida. Por favor, inicia sesión de nuevo.", "warning")
                session.pop('token', None) # Limpiar el token inválido de la sesión
                return jsonify({'success': False, 'message': 'Sesión inválida. Redirigiendo a login.'}), 401 # O redirigir directamente si prefieres
            return jsonify({'success': False, 'message': error_data.get('message', 'Error al actualizar detalles del curso.'), 'errors': error_data.get('errors', {})}), status_code
        except json.JSONDecodeError:
            return jsonify({'success': False, 'message': f"Error desconocido al actualizar detalles del curso: {e.response.text}"}), status_code
    except requests.exceptions.RequestException as e:
        # Manejo de errores de conexión con la API de Laravel
        app.logger.error(f"Error de conexión al actualizar detalles del curso {curso_id}: {e}")
        return jsonify({'success': False, 'message': 'Error de conexión con el servidor de la API.'}), 500
    except Exception as e:
        # Captura cualquier otra excepción inesperada
        app.logger.error(f"Error inesperado al editar detalles del curso {curso_id}: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'Ocurrió un error inesperado al guardar los detalles.'}), 500



@app.route("/cursos/<int:id>/eliminar", methods=["POST"])
def eliminar_curso(id):
    """
    Maneja la eliminación de un curso (solo para el tutor que lo publicó o admin).
    Retorna una respuesta JSON para solicitudes AJAX del modal.
    """
    # Detectar si la solicitud es AJAX (del modal)
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
    current_user_data = session['user'] # Obtener los datos del usuario de la sesión

    # Verificar permisos antes de eliminar
    try:
        app.logger.info(f"Verificando permisos para eliminar curso {id} para usuario {current_user_data.get('id')}.")
        curso_response = requests.get(f"{API_URL_BASE}/cursos/{id}", headers=headers)
        curso_response.raise_for_status() # Lanza un HTTPError si el código de estado es 4xx/5xx

        curso_data = curso_response.json()
        
        # Verificar si el usuario es admin o el tutor propietario del curso
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
            pass # Usar el mensaje de error predeterminado si la respuesta no es JSON

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
    
    # Si los permisos son válidos, proceder con la eliminación
    try:
        app.logger.info(f"Enviando solicitud DELETE a la API para curso {id}.")
        # Laravel's destroy method typically expects a DELETE request
        response = requests.delete(f"{API_URL_BASE}/cursos/{id}", headers=headers)
        response.raise_for_status() # Lanza un HTTPError para códigos de estado 4xx/5xx

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
            pass # Usar el mensaje de error predeterminado si la respuesta no es JSON

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

    # Si la solicitud no fue AJAX o si hubo un error no manejado por jsonify, redirigir
    if not is_ajax:
        return redirect(url_for("cursos"))
    # Si es AJAX, los bloques try/except ya habrán retornado un jsonify.
    # Este punto solo se alcanzaría si algo inesperado sucede, pero la lógica está diseñada para no llegar aquí en AJAX.

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
    data = {"curso_id": curso_id} # El ID del curso a asignar

    try:
        response = requests.post(f"{API_URL_BASE}/estudiantes/{student_id}/asignar-curso", headers=headers, json=data)

        if response.status_code == 200:
            flash("¡Registrado al curso exitosamente!", "success")
        elif response.status_code == 409: # Conflict, ya registrado
            flash("Ya estás registrado en este curso.", "info")
        else:
            api_data = response.json()
            flash(api_data.get("message", f"Error al registrarse al curso (Código: {response.status_code})."), "danger")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión con la API al registrarse al curso: {e}", "danger")
    except json.JSONDecodeError:
        flash(f"Error al procesar la respuesta de la API al registrarse al curso (Código: {response.status_code}).", "danger")

    return redirect(url_for("cursos"))


# --- Rutas adicionales (ej. home, register, profile) ---
# Asegúrate de tener estas rutas definidas en tu app.py si son referenciadas




@app.route("/logout")
def logout():
    # Si hay un token en la sesión, intentar invalidarlo en la API de Laravel
    if 'token' in session:
        token = session['token']
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        try:
            # Llamar al endpoint de logout de Laravel para invalidar el token de Sanctum
            requests.post(f"{API_URL}/logout", headers=headers)
        except requests.exceptions.RequestException as e:
            # Capturar excepciones de red, pero no impedir el logout local
            print(f"Error al intentar cerrar sesión en la API de Laravel: {e}")
            pass 

    # Limpiar todas las variables de sesión relevantes en Flask
    session.pop('usuario', None)         # Si aún usas esta clave antigua
    session.pop('token', None)           # El token de Sanctum
    session.pop('email_for_2fa', None)   # Email temporal para 2FA
    session.pop('user_name', None)       # Si aún usas esta clave antigua
    session.pop('user', None)            # ¡La clave crucial para el objeto user completo!

    flash("Sesión cerrada con éxito.", "info") # Mensaje flash más descriptivo
    return redirect(url_for("login"))




@app.route("/profile", methods=["GET", "POST"])
def profile():
    
    if 'token' in session:
        
        usuario_email = session.get('usuario', 'Usuario') 

        if request.method == "POST":
            
            
            flash("Funcionalidad de actualización de perfil no implementada completamente.")
            return redirect(url_for("profile"))

        return render_template("profile.html", usuario=usuario_email) 
    else:
        flash("Por favor, inicia sesión.")
        return redirect(url_for("login"))


# --- Gestión de usuarios (solo admin) ---
@app.route("/usuarios", methods=["GET"])
def usuarios():
    # Verificar autenticación y rol admin
    if 'token' not in session or 'user' not in session:
        flash("Debes iniciar sesión como administrador para acceder a la gestión de usuarios.", "danger")
        return redirect(url_for("login"))
    current_user = session['user']
    if not has_role_helper(current_user, 'administrador'):
        flash("Acceso denegado: solo administradores.", "danger")
        return redirect(url_for("cursos"))
    # Consumir API de Laravel para obtener usuarios
    headers = {"Authorization": f"Bearer {session['token']}", "Accept": "application/json"}
    try:
        response = requests.get(f"{API_URL_BASE}/users", headers=headers)
        if response.status_code == 200:
            usuarios = response.json()
            return render_template("usuarios.html", usuarios=usuarios)
        else:
            flash(f"Error al obtener usuarios: {response.status_code}", "danger")
            return render_template("usuarios.html", usuarios=[])
    except Exception as e:
        flash(f"Error de conexión con la API: {e}", "danger")
        return render_template("usuarios.html", usuarios=[])

@app.route("/usuarios/nuevo", methods=["GET", "POST"])
def nuevo_usuario():
    # Verificar autenticación y rol admin
    if 'token' not in session or 'user' not in session:
        flash("Debes iniciar sesión como administrador.", "danger")
        return redirect(url_for("login"))
    current_user = session['user']
    if not has_role_helper(current_user, 'administrador'):
        flash("Acceso denegado: solo administradores.", "danger")
        return redirect(url_for("cursos"))
    
    if request.method == "POST":
        headers = {"Authorization": f"Bearer {session['token']}", "Accept": "application/json", "Content-Type": "application/json"}
        
        # Obtener datos del formulario
        data = {
            "name": request.form.get("name"),
            "last_name": request.form.get("last_name"),
            "number": request.form.get("number"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
            "password_confirmation": request.form.get("password_confirmation"),  # <-- ¡IMPORTANTE!
            "role_names": request.form.getlist("roles")
        }
        
        try:
            response = requests.post(f"{API_URL_BASE}/users", headers=headers, json=data)
            if response.status_code == 201:
                flash("Usuario creado exitosamente.", "success")
                return redirect(url_for("usuarios"))
            else:
                error_data = response.json()
                flash(f"Error al crear usuario: {error_data.get('message', 'Error desconocido')}", "danger")
                return render_template("nuevo_usuario.html", data=data, error=error_data)
        except Exception as e:
            flash(f"Error de conexión: {e}", "danger")
            return render_template("nuevo_usuario.html", data=data)
    
    # GET: mostrar formulario
    return render_template("nuevo_usuario.html")

@app.route("/usuarios/<int:id>", methods=["GET"])
def ver_usuario(id):
    # Verificar autenticación y rol admin
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
            return render_template("ver_usuario.html", usuario=usuario)
        else:
            flash("Usuario no encontrado.", "danger")
            return redirect(url_for("usuarios"))
    except Exception as e:
        flash(f"Error de conexión: {e}", "danger")
        return redirect(url_for("usuarios"))

@app.route("/usuarios/<int:id>/editar", methods=["GET", "POST"])
def editar_usuario(id):
    # Verificar autenticación y rol admin
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
        
        # Obtener datos del formulario (AJAX o normal)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = request.get_json()
            print(f"DEBUG - Datos recibidos via AJAX: {data}")  # Debug
        else:
            data = {
                "name": request.form.get("name"),
                "last_name": request.form.get("last_name"),
                "number": request.form.get("number"),
                "email": request.form.get("email"),
                "role_names": request.form.getlist("roles")
            }
            # Solo incluir password si se proporcionó uno nuevo
            password = request.form.get("password")
            if password:
                data["password"] = password
        
        try:
            response = requests.put(f"{API_URL_BASE}/users/{id}", headers=headers, json=data)
            if response.status_code == 200:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({"success": True, "message": "Usuario actualizado exitosamente."})
                flash("Usuario actualizado exitosamente.", "success")
                return redirect(url_for("usuarios"))
            else:
                error_data = response.json()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({"success": False, "message": error_data.get('message', 'Error desconocido'), "errors": error_data.get('errors', {})}), response.status_code
                flash(f"Error al actualizar usuario: {error_data.get('message', 'Error desconocido')}", "danger")
                # Obtener datos actuales del usuario para mostrar en el formulario
                user_response = requests.get(f"{API_URL_BASE}/users/{id}", headers=headers)
                if user_response.status_code == 200:
                    usuario = user_response.json()
                    return render_template("editar_usuario.html", usuario=usuario, error=error_data)
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"success": False, "message": f"Error de conexión: {e}"}), 500
            flash(f"Error de conexión: {e}", "danger")
    
    # GET: obtener datos del usuario y mostrar formulario
    try:
        response = requests.get(f"{API_URL_BASE}/users/{id}", headers=headers)
        if response.status_code == 200:
            usuario = response.json()
            return render_template("editar_usuario.html", usuario=usuario)
        else:
            flash("Usuario no encontrado.", "danger")
            return redirect(url_for("usuarios"))
    except Exception as e:
        flash(f"Error de conexión: {e}", "danger")
        return redirect(url_for("usuarios"))

@app.route("/usuarios/<int:id>/eliminar", methods=["POST"])
def eliminar_usuario(id):
    # Verificar autenticación y rol admin
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
        else:
            error_data = response.json()
            flash(f"Error al eliminar usuario: {error_data.get('message', 'Error desconocido')}", "danger")
    except Exception as e:
        flash(f"Error de conexión: {e}", "danger")
    
    return redirect(url_for("usuarios"))


if __name__ == '__main__':
    
    app.run(debug=True, host='127.0.0.1', port=5000)
