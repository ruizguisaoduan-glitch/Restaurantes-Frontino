from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "clave_secreta123"   # Necesario para sesiones


# -------------------------------
# FUNCIÓN CONECTAR A SQLITE
# -------------------------------
def conectar():
    return sqlite3.connect("database.db")

# -------------------------------
# CREAR BASE DE DATOS
# -------------------------------
conn = conectar()
cursor = conn.cursor()

# Tabla restaurantes
cursor.execute("""
CREATE TABLE IF NOT EXISTS restaurantes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    direccion TEXT,
    telefono TEXT,
    apertura time,
    cierre time

  
)
""")

# Tabla usuarios
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE,
    password TEXT
)
""")

# Crear usuario admin por defecto
cursor.execute("""
INSERT OR IGNORE INTO usuarios (usuario, password)
VALUES ("admin", "1234")
""")

conn.commit()
conn.close()


# -----------------------------------
# RUTA PRINCIPAL - SOLO VISUAL (CLIENTE)
# -----------------------------------
@app.route("/")
def inicio():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM restaurantes")
    datos = cursor.fetchall()
    conn.close()

    # El cliente NO ve botones de admin
    es_admin = "usuario" in session
    return render_template("index.html", restaurantes=datos, admin=es_admin)


# -----------------------------------
# LOGIN ADMIN
# -----------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["usuario"]
        password = request.form["password"]

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND password=?", (user, password))
        datos = cursor.fetchone()
        conn.close()

        if datos:
            session["usuario"] = user
            return redirect("/admin")
        else:
            return render_template("login.html", error="Usuario o contraseña incorrectos")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect("/")


# -----------------------------------
# PANEL ADMIN - SOLO SI HAY LOGIN
# -----------------------------------
@app.route("/admin")
def admin():
    if "usuario" not in session:
        return redirect("/login")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM restaurantes")
    datos = cursor.fetchall()
    conn.close()

    return render_template("admin.html", restaurantes=datos)


# -----------------------------------
# AGREGAR RESTAURANTE (ADMIN)
# -----------------------------------
@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if "usuario" not in session:
        return redirect("/login")

    if request.method == "POST":
        nombre = request.form["nombre"]
        direccion = request.form["direccion"]
        telefono = request.form["telefono"]
        apertura = request.form["apertura"]
        cierre = request.form["cierre"]

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO restaurantes (nombre, direccion, telefono, apertura, cierre) VALUES (?,?,?,?,?)",
                       (nombre, direccion, telefono,apertura, cierre))
        conn.commit()
        conn.close()

        return redirect("/admin")

    return render_template("agregar.html")


# -----------------------------------
# EDITAR RESTAURANTE (ADMIN)
# -----------------------------------
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if "usuario" not in session:
        return redirect("/login")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        direccion = request.form["direccion"]
        telefono = request.form["telefono"]

        cursor.execute("""
        UPDATE restaurantes SET nombre=?, direccion=?, telefono=? WHERE id=?
        """, (nombre, direccion, telefono, id))
        conn.commit()
        conn.close()
        return redirect("/admin")

    cursor.execute("SELECT * FROM restaurantes WHERE id=?", (id,))
    restaurante = cursor.fetchone()
    conn.close()

    return render_template("editar.html", restaurante=restaurante)


# -----------------------------------
# ELIMINAR RESTAURANTE (ADMIN)
# -----------------------------------
@app.route("/eliminar/<int:id>")
def eliminar(id):
    if "usuario" not in session:
        return redirect("/login")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM restaurantes WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin")


if __name__ == "__main__":
    app.run(debug=True)
