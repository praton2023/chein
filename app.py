from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from functools import wraps
import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = "LAB_ONLY_CHANGE_ME"
DB = "lab.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT NOT NULL,
            address TEXT NOT NULL,
            card_number TEXT NOT NULL,
            card_expiry TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL
        );
        """
    )

    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        conn.executemany(
            """
            INSERT INTO users
            (username, password, role, full_name, address, card_number, card_expiry)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """ ,
            [
                ("alice", "alice123", "Cliente", "Alice García", "Calle Ficticia 12, Madrid", "4111111111111111", "12/29"),
                ("bruno", "bruno123", "Cliente", "Bruno Martín", "Avenida Laboratorio 8, Madrid", "5555555555554444", "09/28"),
                ("carla", "carla123", "Cliente", "Carla López", "Calle CTF 44, Madrid", "378282246310005", "06/30"),
                ("tecnico", "tecnico123", "Técnico", "Diego Torres", "Calle Servidores 7, Madrid", "6011111111111117", "03/29"),
            ],
        )

    if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO products (name, description, price) VALUES (?, ?, ?)",
            [
                ("Auriculares CTF", "Auriculares inalámbricos para el laboratorio.", 49.99),
                ("Teclado Mecánico", "Teclado mecánico compacto.", 79.90),
                ("Ratón Óptico", "Ratón óptico de pruebas.", 24.50),
                ("Monitor 24 pulgadas", "Monitor Full HD de laboratorio.", 139.99),
                ("USB de Pruebas", "Memoria USB ficticia para el laboratorio.", 12.00),
            ],
        )

    conn.commit()
    conn.close()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def current_user():
    username = session.get("username")
    if not username:
        return None
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return user


@app.context_processor
def inject_current_user():
    return {"current_user": current_user()}


@app.route("/")
def index():
    conn = get_db()
    products = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
    conn.close()
    return render_template("index.html", products=products)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()
        conn.close()

        if user:
            session["username"] = user["username"]
            return redirect(url_for("index"))

        return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/profile/<username>", methods=["GET", "POST"])
@login_required
def profile(username):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    if not user:
        conn.close()
        return render_template("forbidden.html", message="Perfil no encontrado"), 404

    if request.method == "POST":
        # La interfaz normal solo permite editar datos personales.
        # El campo role NO se acepta aquí.
        address = request.form.get("address", "")
        card_number = request.form.get("card_number", "")
        card_expiry = request.form.get("card_expiry", "")

        conn.execute(
            """
            UPDATE users
            SET address = ?, card_number = ?, card_expiry = ?
            WHERE username = ?
            """,
            (address, card_number, card_expiry, username),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("profile", username=username))

    conn.close()
    return render_template("profile.html", user=user)


@app.route("/api/user/update", methods=["POST"])
@login_required
def api_user_update():
    """DELIBERATE VULNERABILITY: mass assignment / missing authorization.

    This endpoint is not linked from the normal UI. It accepts the sensitive
    role attribute directly from the client and does not verify whether the
    caller is authorized to change it.
    """
    data = request.get_json(silent=True) or request.form
    user_id = data.get("id", "")
    address = data.get("address", "")
    card_number = data.get("card_number", "")
    card_expiry = data.get("card_expiry", "")
    role = data.get("role", "")

    if not user_id:
        return {"error": "Falta el parámetro id"}, 400

    conn = get_db()
    target = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not target:
        conn.close()
        return {"error": "Usuario no encontrado"}, 404

    # Vulnerabilidad intencionada: no se comprueba que el usuario pueda
    # modificar el rol ni que el atributo role deba ser solo servidor-side.
    conn.execute(
        """
        UPDATE users
        SET address = ?, card_number = ?, card_expiry = ?, role = ?
        WHERE id = ?
        """,
        (address, card_number, card_expiry, role, user_id),
    )
    conn.commit()
    conn.close()

    return {
        "status": "updated",
        "user_id": user_id,
        "role": role,
        "note": "Endpoint deliberadamente vulnerable para el CTF local.",
    }


@app.route("/technician")
@login_required
def technician():
    requested_role = request.headers.get("X-Role", "")

    if requested_role != "technician":
        app.logger.warning(f"Technician access DENIED: user={session.get('username')} X-Role={requested_role!r}")
        return render_template("forbidden.html"), 403

    app.logger.warning(f"Technician access GRANTED: user={session.get('username')} X-Role={requested_role!r}")

    conn = get_db()

    users = conn.execute("""
        SELECT id, username, full_name, address, card_number, card_expiry, role
        FROM users
        ORDER BY id
    """).fetchall()

    conn.close()

    return render_template("technician.html", users=users)


@app.route("/products/search")
def search_products():
    q = request.args.get("q", "")
    conn = get_db()

    # DELIBERATE VULNERABILITY: SQL injection from the search box.
    # A crafted value can close the LIKE string and append another SQL
    # statement. The endpoint then re-reads the products so the result
    # visibly reflects persistent changes to the database.
    script = "SELECT * FROM products WHERE name LIKE '%" + q + "%'"
    error = None

    try:
        conn.executescript(script)
        products = conn.execute(
            "SELECT * FROM products WHERE name LIKE ? ORDER BY id",
            (f"%{q}%",),
        ).fetchall()
    except sqlite3.Error as exc:
        products = []
        error = str(exc)

    conn.close()
    return render_template("search.html", products=products, q=q, error=error)


@app.route("/admin/products")
def admin_products():
    conn = get_db()
    products = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
    conn.close()
    return render_template("admin_products.html", products=products)


@app.route("/osint")
def osint():
    return render_template("osint.html")


@app.route("/social/reddit")
def social_reddit():
    return render_template("reddit.html")


@app.route("/social/x")
def social_x():
    return render_template("x.html")


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
