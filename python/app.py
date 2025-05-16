from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests

# Configuración de la API
BASE_URL = "http://127.0.0.1:8000/api"

app = Flask(__name__)
app.secret_key = "super_secret_key"  # Cambiar por una clave más segura en producción


@app.route("/")
def home():
    """Página de inicio"""
    if "token" in session:
        return render_template("dashboard.html", user=session.get("user"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Manejo del inicio de sesión"""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            payload = {"email": email, "contraseña": password, "contraseña_confirmation": password}
            response = requests.post(f"{BASE_URL}/login", json=payload)
            data = response.json()

            if response.status_code == 200:
                session["token"] = data["token"]
                session["user"] = data["usuario"]
                flash("Inicio de sesión exitoso", "success")
                return redirect(url_for("home"))
            else:
                flash(data.get("message", "Error en el inicio de sesión"), "danger")

        except Exception as e:
            flash(f"Error de conexión: {e}", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Manejo del registro de usuarios"""
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Las contraseñas no coinciden", "danger")
            return redirect(url_for("register"))

        try:
            payload = {
                "nombre": name,
                "email": email,
                "contraseña": password,
                "contraseña_confirmation": confirm_password,
            }
            response = requests.post(f"{BASE_URL}/register", json=payload)
            data = response.json()

            if response.status_code == 201:
                flash("Usuario registrado exitosamente", "success")
                return redirect(url_for("login"))
            else:
                flash(data.get("message", "Error en el registro"), "danger")

        except Exception as e:
            flash(f"Error de conexión: {e}", "danger")

    return render_template("register.html")


@app.route("/logout")
def logout():
    """Cierre de sesión"""
    if "token" in session:
        try:
            headers = {"Authorization": f"Bearer {session['token']}"}
            response = requests.post(f"{BASE_URL}/logout", headers=headers)
            if response.status_code == 200:
                session.clear()
                flash("Sesión cerrada exitosamente", "success")
            else:
                flash("Error al cerrar sesión", "danger")
        except Exception as e:
            flash(f"Error de conexión: {e}", "danger")
    else:
        flash("No has iniciado sesión", "warning")

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
