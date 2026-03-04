from flask import jsonify, request
from database import get_db_connection

def register_routes(app):

    @app.route("/")
    def home():
        return "Backend API running!"

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

        return jsonify({"message": "User created"}), 201


    @app.route("/users", methods=["GET"])
    def get_users():
        conn = get_db_connection()

        users = conn.execute(
            "SELECT * FROM users"
        ).fetchall()

        conn.close()

        return jsonify([dict(user) for user in users])