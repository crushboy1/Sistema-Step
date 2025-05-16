from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import zeep  
import json 
import re 
import datetime 

app = Flask(__name__)
app.secret_key = 'clave_secreta'  


API_URL = "http://localhost:8000/api"
API_URL_BASE = "http://127.0.0.1:8000/api/v1" 


WEB_URL = "http://localhost:8000/api/v1/soap"
WEB_URL_BASE = "http://localhost:8000/api/v1/soap_cursos"


RECAPTCHA_SITE_KEY = '6Ld6ey0rAAAAAJp4boxN3CzM-VjsPKjK-bZLVPiU'
RECAPTCHA_SECRET_KEY = '6Ld6ey0rAAAAANZkkDMFnTkcLRfA5R2skbv5LXBQ'


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

        
        data = {
            'secret': RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        response = requests.post(verify_url, data=data)
        result = response.json()

        if result.get('success'): 

        
            api_response = requests.post(f"{API_URL}/login", json={"email": email, "password": password})

            
            print("API Response Status Code:", api_response.status_code)
            print("API Response Content:", api_response.text)

            
            try:
                api_data = api_response.json()

                if api_response.status_code == 200:
                    
                    if api_data.get('requires_2fa'):
                        
                        session['email_for_2fa'] = api_data.get('email', email) 
                        flash("Se ha enviado un código de verificación a su correo.")
                        
                        return redirect(url_for("verify_2fa"))
                    else:
                        
                        if 'token' in api_data:
                            session['token'] = api_data['token']  
                            
                            flash("Inicio de sesión exitoso")
                            return redirect(url_for("estudiantes"))
                        else:
                            
                            flash("Respuesta de API inesperada después de login exitoso.")
                            return redirect(url_for("login"))


                elif api_response.status_code == 401:
                    
                    flash(api_data.get("message", "Credenciales inválidas"))
                    return redirect(url_for("login"))
                else:
                    
                    flash(api_data.get("message", f"Error desconocido al iniciar sesión (Código: {api_response.status_code})"))
                    return redirect(url_for("login"))

            except json.JSONDecodeError:
                
                flash(f"Error al procesar la respuesta de la API (Código: {api_response.status_code}).")
                return redirect(url_for("login"))

        else:
            
            flash("Error de CAPTCHA. Por favor, intenta nuevamente.")
            return redirect(url_for("login"))

    
    return render_template("login.html", recaptcha_site_key=RECAPTCHA_SITE_KEY)


@app.route("/verify-2fa", methods=["GET", "POST"])
def verify_2fa():
    
    if 'email_for_2fa' not in session:
        flash("Por favor, inicie sesión primero para verificar su cuenta.")
        return redirect(url_for("login"))

    if request.method == "POST":
        verification_code = request.form.get("verification_code")
        email = session.get('email_for_2fa') 

        
        if not email:
            flash("Error en el proceso de verificación. Por favor, inicie sesión nuevamente.")
            return redirect(url_for("login"))

        
        api_response = requests.post(f"{API_URL}/verifyCode", json={
            "email": email,
            "code": verification_code
        })

        
        print("Verify 2FA API Response Status Code:", api_response.status_code)
        print("Verify 2FA API Response Content:", api_response.text)

        
        try:
            api_data = api_response.json()

            if api_response.status_code == 200:
                
                if 'token' in api_data:
                    
                    session['token'] = api_data['token']
                    session['usuario'] = api_data.get('user', {}).get('email', email) 
                    session['user_name'] = api_data.get('user', {}).get('name', 'Usuario')
                    flash("Código verificado exitosamente. Inicio de sesión completo.", "success")
                    
                    session.pop('email_for_2fa', None)
                    
                    return redirect(url_for("estudiantes"))
                else:
                    
                    flash("Verificación exitosa, pero la API no devolvió un token.")
                    return redirect(url_for("verify_2fa")) 
                    

            else: 
                flash(api_data.get("message", f"Error al verificar el código (Código: {api_response.status_code})."))
                
                return redirect(url_for("verify_2fa"))

        except json.JSONDecodeError:
            
            flash(f"Error al procesar la respuesta de verificación de la API (Código: {api_response.status_code}).")
            return redirect(url_for("verify_2fa"))



    return render_template("verify_2fa.html")


@app.route("/resend-2fa-code", methods=["POST"]) 
def resend_2fa_code():
    print("--- Resend 2FA Code Route ---")
    print("Request Method:", request.method)
    print("Session before resend_2fa_code:", dict(session)) 

    
    if 'email_for_2fa' not in session:
        flash("Por favor, inicie sesión primero para solicitar un nuevo código.", "warning")
        print("Session missing email_for_2fa in resend route, redirecting to login:", dict(session)) 
        return redirect(url_for("login"))

    email = session.get('email_for_2fa') 

    
    if not email:
        flash("Error al solicitar el reenvío. Por favor, inicie sesión nuevamente.", "danger")
        print("Email missing from session in resend route, redirecting to login:", dict(session)) 
        return redirect(url_for("login"))

    
    
    try:
        
        
        api_response = requests.post(f"{API_URL}/resendCode", json={"email": email})

        
        print("Resend 2FA API Response Status Code:", api_response.status_code)
        print("Resend 2FA API Response Content:", api_response.text)

        if api_response.status_code == 200:
            
            
            try:
                api_data = api_response.json()
                flash(api_data.get("message", "Se ha reenviado un nuevo código de verificación a su correo."), "success")
            except json.JSONDecodeError:
                 flash("Se ha reenviado un nuevo código de verificación a su correo.", "success")

        else:
            
            try:
                api_data = api_response.json()
                flash(api_data.get("message", f"Error al reenviar el código (Código: {api_response.status_code})."), "danger")
            except json.JSONDecodeError:
                flash(f"Error al reenviar el código (Código: {api_response.status_code}, respuesta no JSON).", "danger")

    except requests.exceptions.RequestException as e:
        
        flash(f"Error de conexión al intentar reenviar el código: {e}", "danger")

    print("Session after resend logic:", dict(session)) 
    
    return redirect(url_for("verify_2fa"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
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
                "name": nombre, 
                "email": email,
                "password": password,
                "password_confirmation": password_confirmation
            })

            
            
            print("Register API Response Status Code:", api_response.status_code)
            print("Register API Response Content:", api_response.text)

            
            if api_response.status_code == 201:
                flash("Registro exitoso, por favor inicia sesión.")
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

                    flash(error_message)

                except json.JSONDecodeError:
                    
                    flash(f"Error al procesar errores de validación de la API (Código: 422, respuesta no JSON).")

                
                return redirect(url_for("register"))

            
            else:
                try:
                    api_data = api_response.json()
                    
                    error_message = api_data.get("message", f"Error al registrar usuario (Código: {api_response.status_code})")
                    flash(error_message)

                except json.JSONDecodeError:
                    
                    flash(f"Error al procesar la respuesta de registro de la API (Código: {api_response.status_code}).")

                
                return redirect(url_for("register"))

        else:
            
            flash("Error de CAPTCHA. Por favor, intenta nuevamente.")
            return redirect(url_for("register"))

    
    
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
    
    if 'token' not in session:
        flash("Por favor, inicia sesión.")
        return redirect(url_for("login"))

    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}

    
    query = request.args.get("q", "").strip().lower()

    
    
    response = requests.get(f"{API_URL_BASE}/cursos", headers=headers)

    if response.status_code == 200:
        try:
            cursos = response.json()

            
            if query:
                cursos = [
                    curso for curso in cursos
                    if query in curso.get("nombre", "").lower() or query in curso.get("descripcion", "").lower() 
                ]

            return render_template("cursos.html", cursos=cursos)
        except json.JSONDecodeError:
            flash("Error al procesar la lista de cursos recibida de la API.")
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
                flash(api_data.get("message", f"Error al cargar los cursos (Código: {response.status_code})."))
            except json.JSONDecodeError:
                flash(f"Error al cargar los cursos (Código: {response.status_code}, respuesta no JSON).")

            return redirect(url_for("home"))



@app.route("/cursos/<int:id>", methods=["GET"])
def ver_curso(id):
    if 'token' not in session:
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("login"))

    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_URL_BASE}/cursos/{id}", headers=headers)

    if response.status_code == 200:
        try:
            curso = response.json()
            return render_template("ver_curso.html", curso=curso)
        except json.JSONDecodeError:
            flash("Error al procesar la información del curso recibida de la API.", "danger")
            return redirect(url_for("cursos"))
    else:
        try:
            api_data = response.json()
            flash(api_data.get("message", f"No se pudo cargar la información del curso (Código: {response.status_code})."), "danger")
        except json.JSONDecodeError:
            flash(f"No se pudo cargar la información del curso (Código: {response.status_code}, respuesta no JSON).", "danger")

        return redirect(url_for("cursos"))



@app.route("/cursos/nuevo", methods=["GET", "POST"])
def nuevo_curso():
    if 'token' not in session:
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("login"))

    token = session['token']
     
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "text/xml"}

    if request.method == "POST":
        nombre = request.form.get("nombre")
        descripcion = request.form.get("descripcion")
        creditos = request.form.get("creditos")

        
         
        payload = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:App\Http\Controllers">
           <soapenv:Header/>
           <soapenv:Body>
              <urn:crearCurso>
                 <nombre>{nombre}</nombre>
                 <descripcion>{descripcion}</descripcion>
                 <creditos>{creditos}</creditos>
              </urn:crearCurso>
           </soapenv:Body>
        </soapenv:Envelope>
        """

        
        
        response = requests.post(WEB_URL_BASE, headers=headers, data=payload)

        if response.status_code == 200:
            
            
            if "id" in response.text:  
                flash("Curso creado con éxito.", "success")
                return redirect(url_for("cursos"))  
            else:
                 
                flash("Error al crear el curso. Verifica los datos o la respuesta del servicio SOAP.", "danger")
                 
                
        else:
            flash(f"Error al conectar con el servicio SOAP. Código de estado: {response.status_code}", "danger")
            
            


    
    return render_template("nuevo_curso.html")


@app.route("/cursos/<int:id>/editar", methods=["GET", "POST"])
def editar_curso(id):
    if 'token' not in session:
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("login"))

    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}

    if request.method == "POST":
        data = {
            "nombre": request.form.get("nombre"),
            "descripcion": request.form.get("descripcion"),
            "creditos": request.form.get("creditos"),
        }
        
        response = requests.put(f"{API_URL_BASE}/cursos/{id}", headers=headers, json=data)

        if response.status_code == 200:
            flash("Curso actualizado con éxito.", "success")
            return redirect(url_for("cursos"))
        else:
            try:
                api_data = response.json()
                flash(api_data.get("message", f"Error al actualizar el curso (Código: {response.status_code})."), "danger")
            except json.JSONDecodeError:
                 flash(f"Error al actualizar el curso (Código: {response.status_code}, respuesta no JSON).", "danger")


    
    response = requests.get(f"{API_URL_BASE}/cursos/{id}", headers=headers)
    if response.status_code == 200:
        try:
            curso = response.json()
            return render_template("editar_curso.html", curso=curso)
        except json.JSONDecodeError:
            flash("Error al procesar la información del curso para editar.", "danger")
            return redirect(url_for("cursos"))
    else:
        try:
            api_data = response.json()
            flash(api_data.get("message", f"No se pudo cargar la información del curso para editar (Código: {response.status_code})."), "danger")
        except json.JSONDecodeError:
             flash(f"No se pudo cargar la información del curso para editar (Código: {response.status_code}, respuesta no JSON).", "danger")

        return redirect(url_for("cursos"))



@app.route("/cursos/<int:id>/eliminar", methods=["POST"])
def eliminar_curso(id):
    if 'token' not in session:
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("login"))

    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(f"{API_URL_BASE}/cursos/{id}", headers=headers)

    if response.status_code == 200:
        flash("Curso eliminado con éxito.", "success")
    else:
        try:
            api_data = response.json()
            flash(api_data.get("message", f"No se pudo eliminar el curso (Código: {response.status_code})."), "danger")
        except json.JSONDecodeError:
             flash(f"No se pudo eliminar el curso (Código: {response.status_code}, respuesta no JSON).", "danger")

    return redirect(url_for("cursos"))


@app.route("/logout")
def logout():
    
    
    if 'token' in session:
        token = session['token']
        headers = {"Authorization": f"Bearer {token}"}
        try:
            
            requests.post(f"{API_URL}/logout", headers=headers)
        except:
            
            pass 

    
    session.pop('usuario', None) 
    session.pop('token', None)  
    session.pop('email_for_2fa', None) 
    session.pop('user_name', None)
    flash("Sesión cerrada con éxito.")
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


if __name__ == '__main__':
    
    app.run(debug=True, host='127.0.0.1', port=5000)
