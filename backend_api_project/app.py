"""
File: app.py
Project: Backend API Project
Description:
    Flask API connected with SQLite database.
"""

from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DATABASE = "database.db"


# -------------------------------
# Database Connection
# -------------------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------------
# Initialize Database
# -------------------------------
def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()


init_db()


# -------------------------------
# Routes
# -------------------------------

@app.route("/")
def home():
    return "Backend API running successfully!"


# CREATE
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    if not data or "name" not in data or "age" not in data:
        return jsonify({"error": "Invalid input"}), 400

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO users (name, age) VALUES (?, ?)",
        (data["name"], data["age"])
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "User added successfully"}), 201


# READ

# Get all users
@app.route("/users", methods=["GET"])
def get_users():
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return jsonify([dict(user) for user in users])

# Get one user by ID
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()

    if user is None:
        return jsonify({"error": "User not found"}), 404

    return jsonify(dict(user))


# UPDATE USER
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()

    if not data or "name" not in data or "age" not in data:
        return jsonify({"error": "Invalid input"}), 400

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    if user is None:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    conn.execute(
        "UPDATE users SET name = ?, age = ? WHERE id = ?",
        (data["name"], data["age"], user_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "User updated successfully"})

# DELETE USER
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    if user is None:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "User deleted successfully"})

if __name__ == "__main__":
    app.run(debug=True)