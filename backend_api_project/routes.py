from flask import jsonify, request
from database import get_db_connection


def register_routes(app):

    @app.route("/")
    def home():
        return "Backend API running!"

    # CREATE USER
    @app.route("/users", methods=["POST"])
    def create_user():
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        name = data.get("name")
        age = data.get("age")

        if not name or not isinstance(name, str):
            return jsonify({"error": "Valid name is required"}), 400

        if age is None or not isinstance(age, int):
            return jsonify({"error": "Age must be an integer"}), 400

        if age <= 0:
            return jsonify({"error": "Age must be positive"}), 400

        conn = get_db_connection()

        conn.execute(
            "INSERT INTO users (name, age) VALUES (?, ?)",
            (name, age)
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "User created successfully"}), 201


    # GET ALL USERS
    @app.route("/users", methods=["GET"])
    def get_users():
        conn = get_db_connection()

        users = conn.execute(
            "SELECT * FROM users"
        ).fetchall()

        conn.close()

        return jsonify([dict(user) for user in users])


    # UPDATE USER
    @app.route("/users/<int:user_id>", methods=["PUT"])
    def update_user(user_id):
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        name = data.get("name")
        age = data.get("age")

        if not name or not isinstance(name, str):
            return jsonify({"error": "Valid name required"}), 400

        if age is None or not isinstance(age, int):
            return jsonify({"error": "Age must be an integer"}), 400

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        if user is None:
            conn.close()
            return jsonify({"error": "User not found"}), 404

        conn.execute(
            "UPDATE users SET name = ?, age = ? WHERE id = ?",
            (name, age, user_id)
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "User updated successfully"})


    # DELETE USER
    @app.route("/users/<int:user_id>", methods=["DELETE"])
    def delete_user(user_id):

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        if user is None:
            conn.close()
            return jsonify({"error": "User not found"}), 404

        conn.execute(
            "DELETE FROM users WHERE id = ?",
            (user_id,)
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "User deleted successfully"})