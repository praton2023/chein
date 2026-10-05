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
            price REAL NOT NULL,
            category TEXT NOT NULL
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
                ("tecnico", "tecnico123", "technician", "Diego Torres", "Calle Servidores 7, Madrid", "6011111111111117", "03/29"),
            ],
        )

    if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO products (name, description, price, category) VALUES (?, ?, ?, ?)",
            [
            ("Teléfono Móvil", "Smartphone de última generación", 299.99, "electronica"),
            ("Ordenador Portátil", "Portátil para trabajo y gaming", 899.50, "electronica"),
            ("Auriculares Bluetooth", "Auriculares inalámbricos para el laboratorio.", 49.99, "electronica"),
            ("Televisor Smart TV", "Smart TV 55 pulgadas 4K", 450.00, "electronica"),
            ("Tablet", "Tablet de 10 pulgadas ligera", 199.99, "electronica"),
            ("Ratón Inalámbrico", "Ratón óptico de pruebas.", 24.50, "electronica"),
            ("Teclado Mecánico", "Teclado mecánico compacto.", 79.90, "electronica"),
            ("Monitor 24 pulgadas", "Monitor Full HD de laboratorio.", 139.99, "electronica"),
            ("USB de Pruebas", "Memoria USB ficticia para el laboratorio.", 12.00, "electronica"),
            ("Altavoz Inteligente", "Altavoz con asistente virtual", 59.99, "electronica"),
            ("Sofá de tres plazas", "Sofá cómodo de tela resistente", 350.00, "hogar"),
            ("Lámpara de pie", "Lámpara de diseño moderno", 45.00, "hogar"),
            ("Mesa de comedor", "Mesa de madera maciza", 250.00, "hogar"),
            ("Silla ergonómica", "Silla para oficina en casa", 120.00, "hogar"),
            ("Alfombra persa", "Alfombra con motivos clásicos", 90.00, "hogar"),
            ("Microondas", "Microondas de 800W", 65.00, "hogar"),
            ("Batidora de vaso", "Batidora para smoothies y salsas", 40.00, "hogar"),
            ("Cuadro decorativo", "Lámina abstracta enmarcada", 35.00, "hogar"),
            ("Espejo de pared", "Espejo redondo con marco de metal", 55.00, "hogar"),
            ("Cojín de terciopelo", "Cojín suave para sofá o cama", 15.00, "hogar"),
            ("Camiseta de algodón", "Camiseta básica de manga corta", 12.00, "ropa"),
            ("Pantalón vaquero", "Vaquero de corte recto azul", 35.00, "ropa"),
            ("Chaqueta de cuero", "Chaqueta estilo motero negra", 120.00, "ropa"),
            ("Zapatillas deportivas", "Zapatillas para running ligeras", 60.00, "ropa"),
            ("Bufanda de lana", "Bufanda gruesa para invierno", 18.00, "ropa"),
            ("Sombrero de paja", "Sombrero ideal para la playa", 15.00, "ropa"),
            ("Guantes de invierno", "Guantes térmicos impermeables", 20.00, "ropa"),
            ("Calcetines estampados", "Pack de 3 calcetines divertidos", 10.00, "ropa"),
            ("Vestido de noche", "Vestido elegante largo", 80.00, "ropa"),
            ("Abrigo largo", "Abrigo de paño clásico", 95.00, "ropa"),
            ("Balón de fútbol", "Balón oficial talla 5", 25.00, "deportes"),
            ("Raqueta de tenis", "Raqueta ligera para principiantes", 85.00, "deportes"),
            ("Bicicleta de montaña", "Bicicleta con doble suspensión", 450.00, "deportes"),
            ("Juego de pesas", "Mancuernas ajustables hasta 20kg", 60.00, "deportes"),
            ("Esterilla de yoga", "Esterilla antideslizante acolchada", 20.00, "deportes"),
            ("Cuerda de saltar", "Cuerda de velocidad ajustable", 12.00, "deportes"),
            ("Botas de senderismo", "Botas impermeables transpirables", 90.00, "deportes"),
            ("Casco de ciclismo", "Casco aerodinámico de seguridad", 45.00, "deportes"),
            ("Guantes de boxeo", "Guantes de entrenamiento 14oz", 35.00, "deportes"),
            ("Bañador de natación", "Bañador resistente al cloro", 22.00, "deportes"),
            ("Muñeca articulada", "Muñeca con varios accesorios", 30.00, "juguetes"),
            ("Coche teledirigido", "Coche 4x4 RC a batería", 45.00, "juguetes"),
            ("Puzzle de 1000 piezas", "Puzzle de paisaje de montaña", 15.00, "juguetes"),
            ("Oso de peluche", "Oso gigante extra suave", 40.00, "juguetes"),
            ("Juego de mesa de estrategia", "Juego de conquista para 4 jugadores", 50.00, "juguetes"),
            ("Bloques de construcción", "Set de 500 piezas coloridas", 35.00, "juguetes"),
            ("Yo-yo luminoso", "Yo-yo dinámico con luces LED", 8.00, "juguetes"),
            ("Peonza de madera", "Peonza clásica con cuerda", 5.00, "juguetes"),
            ("Pizarra mágica", "Pizarra para dibujar y borrar", 18.00, "juguetes"),
            ("Figura de acción", "Figura coleccionable de superhéroe", 25.00, "juguetes"),
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

@app.context_processor
def inject_categorias():
    conn = get_db()
    try:
        categorias_db = conn.execute("SELECT DISTINCT category FROM products").fetchall()
        categorias = [row["category"] for row in categorias_db]
    except sqlite3.OperationalError:
        categorias = []
    finally:
        conn.close()
    
    return {"categorias": categorias}

@app.route("/")
def index():
    conn = get_db()
    products = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
    
    categorias_db = conn.execute("SELECT DISTINCT category FROM products").fetchall()
    categorias = [row["category"] for row in categorias_db]
    
    conn.close()
    return render_template("index.html", products=products, categorias=categorias)

@app.route("/category/<categoria>")
def show_category(categoria):
    conn = get_db()
    products = conn.execute("SELECT * FROM products WHERE category = ? ORDER BY id", (categoria,)).fetchall()
    
    categorias_db = conn.execute("SELECT DISTINCT category FROM products").fetchall()
    categorias = [row["category"] for row in categorias_db]
    
    conn.close()
    return render_template("index.html", products=products, categorias=categorias, categoria_actual=categoria)

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

@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        return render_template("bromita.html", error="Tú no poder registrar,tú tener que ser chino\n切恩万岁")
    return render_template("sign_in.html")

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
    username = session.get("username")

    conn = get_db()
    current_user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()

    if current_user and current_user["role"] == "technician":
        app.logger.info(
            f"Technician access GRANTED (legitimate): "
            f"user={username} role={current_user['role']}"
        )

    else:

        requested_role = request.headers.get("X-Role", "")

        if requested_role != "technician":
            app.logger.warning(
                f"Technician access DENIED: "
                f"user={username} X-Role={requested_role!r}"
            )
            return render_template("forbidden.html"), 403

        app.logger.warning(
            f"Technician access GRANTED via header: "
            f"user={username} X-Role={requested_role!r}"
        )

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
        
    categorias_db = conn.execute("SELECT DISTINCT category FROM products").fetchall()
    categorias = [row["category"] for row in categorias_db]

    conn.close()
    return render_template("search.html", products=products, categorias=categorias, q=q, error=error)

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
