"""API REST de la liste de tâches (Flask + PostgreSQL)."""
import os
from contextlib import closing

import psycopg2
from flask import Flask, jsonify, request
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

COLUMNS = "id, title, done"


def get_connection():
    """Ouvre une connexion à PostgreSQL à partir des variables d'environnement."""
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        dbname=os.environ.get("DB_NAME", "todo"),
        user=os.environ.get("DB_USER", "todo_user"),
        password=os.environ.get("DB_PASSWORD", ""),
        connect_timeout=5,
    )


def query(sql, params=(), fetch="all"):
    """Exécute une requête et valide la transaction."""
    with closing(get_connection()) as conn:
        with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            if fetch == "all":
                return cur.fetchall()
            if fetch == "one":
                return cur.fetchone()
            return None


@app.get("/api/health")
def health():
    return jsonify(status="ok")


@app.get("/api/tasks")
def list_tasks():
    return jsonify(query(f"SELECT {COLUMNS} FROM tasks ORDER BY id"))


@app.post("/api/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    if not title or len(title) > 200:
        return jsonify(error="Le titre est obligatoire (200 caractères maximum)."), 400
    task = query(
        f"INSERT INTO tasks (title) VALUES (%s) RETURNING {COLUMNS}",
        (title,),
        fetch="one",
    )
    return jsonify(task), 201


@app.patch("/api/tasks/<int:task_id>")
def toggle_task(task_id):
    task = query(
        f"UPDATE tasks SET done = NOT done WHERE id = %s RETURNING {COLUMNS}",
        (task_id,),
        fetch="one",
    )
    if task is None:
        return jsonify(error="Tâche introuvable."), 404
    return jsonify(task)


@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    deleted = query(
        "DELETE FROM tasks WHERE id = %s RETURNING id", (task_id,), fetch="one"
    )
    if deleted is None:
        return jsonify(error="Tâche introuvable."), 404
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
