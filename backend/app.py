"""API REST : inscription, connexion et modification du profil (Flask + PostgreSQL)."""
import os
import re
from contextlib import closing
from functools import wraps

import psycopg2
from flask import Flask, g, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from psycopg2 import errors
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("La variable d'environnement SECRET_KEY est obligatoire (voir .env.example).")

serializer = URLSafeTimedSerializer(SECRET_KEY)
TOKEN_MAX_AGE = 8 * 3600  # durée de validité du jeton : 8 heures
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

PROFILE_SQL = (
    "SELECT id, email, full_name, bio, "
    "to_char(created_at, 'YYYY-MM-DD HH24:MI') AS created_at FROM users WHERE id = %s"
)


def get_connection():
    """Ouvre une connexion PostgreSQL à partir des variables d'environnement."""
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        dbname=os.environ.get("DB_NAME", "appdb"),
        user=os.environ.get("DB_USER", "appuser"),
        password=os.environ.get("DB_PASSWORD", ""),
        connect_timeout=5,
    )


def query(sql, params=(), fetch="one"):
    """Exécute une requête, valide la transaction et renvoie le résultat."""
    with closing(get_connection()) as conn:
        with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            if fetch == "all":
                return cur.fetchall()
            if fetch == "one":
                return cur.fetchone()
            return None


def login_required(view):
    """Vérifie le jeton « Authorization: Bearer ... » et place l'identifiant dans g.user_id."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify(error="Authentification requise."), 401
        try:
            g.user_id = serializer.loads(header[7:], max_age=TOKEN_MAX_AGE)
        except SignatureExpired:
            return jsonify(error="Session expirée, reconnectez-vous."), 401
        except BadSignature:
            return jsonify(error="Jeton invalide."), 401
        return view(*args, **kwargs)

    return wrapper


@app.get("/api/health")
def health():
    return jsonify(status="ok")


@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    full_name = str(data.get("full_name", "")).strip()

    if not EMAIL_RE.match(email) or len(email) > 255:
        return jsonify(error="Adresse e-mail invalide."), 400
    if len(password) < 8:
        return jsonify(error="Le mot de passe doit contenir au moins 8 caractères."), 400
    if len(full_name) > 100:
        return jsonify(error="Le nom est trop long (100 caractères maximum)."), 400

    try:
        query(
            "INSERT INTO users (email, password_hash, full_name) VALUES (%s, %s, %s)",
            (email, generate_password_hash(password), full_name),
            fetch=None,
        )
    except errors.UniqueViolation:
        return jsonify(error="Un compte existe déjà avec cette adresse e-mail."), 409
    return jsonify(message="Compte créé. Vous pouvez vous connecter."), 201


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    user = query("SELECT id, password_hash FROM users WHERE email = %s", (email,))
    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify(error="E-mail ou mot de passe incorrect."), 401
    return jsonify(token=serializer.dumps(user["id"]))


@app.get("/api/profile")
@login_required
def get_profile():
    profile = query(PROFILE_SQL, (g.user_id,))
    if profile is None:
        return jsonify(error="Utilisateur introuvable."), 404
    return jsonify(profile)


@app.put("/api/profile")
@login_required
def update_profile():
    data = request.get_json(silent=True) or {}
    full_name = str(data.get("full_name", "")).strip()
    bio = str(data.get("bio", "")).strip()
    if len(full_name) > 100 or len(bio) > 500:
        return jsonify(error="Nom (100 caractères max) ou biographie (500 max) trop long."), 400

    query(
        "UPDATE users SET full_name = %s, bio = %s WHERE id = %s",
        (full_name, bio, g.user_id),
        fetch=None,
    )
    return jsonify(query(PROFILE_SQL, (g.user_id,)))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
