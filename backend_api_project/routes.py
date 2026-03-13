import jwt
import datetime
from functools import wraps
from flask import jsonify, request, current_app
import bcrypt
from flask import jsonify, request
from database import get_db_connection

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return jsonify({"error": "Token missing"}), 401

        try:
            jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return jsonify({"error": "Token missing"}), 401

        try:
            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            if data["role"] != "admin":
                return jsonify({"error": "Admin access required"}), 403

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated

def register_routes(app):

    @app.route("/")
    def home():
        return "Backend API running!"

    # CREATE USER
    @app.route("/users", methods=["POST"])
    def create_user():

        data = request.get_json()
        role = data.get("role", "user")

        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        name = data.get("name")
        age = data.get("age")
        password = data.get("password")   # ← THIS LINE WAS MISSING

        if not name or not isinstance(name, str):
            return jsonify({"error": "Valid name required"}), 400

        if age is None or not isinstance(age, int):
            return jsonify({"error": "Age must be integer"}), 400

        if not password:
            return jsonify({"error": "Password required"}), 400


    # Hash password
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        conn = get_db_connection()

        conn.execute(
            "INSERT INTO users (name, age, password, role) VALUES (?, ?, ?, ?)",
            (name, age, hashed_password, role)
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "User registered successfully"}), 201


    # GET ALL USERS
    @app.route("/users", methods=["GET"])
    @token_required
    def get_users():

        page = request.args.get("page", default=1, type=int)
        limit = request.args.get("limit", default=5, type=int)
        search = request.args.get("search", default="", type=str)

        offset = (page - 1) * limit

        conn = get_db_connection()

        if search:
            users = conn.execute(
                "SELECT * FROM users WHERE name LIKE ? LIMIT ? OFFSET ?",
                (f"%{search}%", limit, offset)
            ).fetchall()
        else:
            users = conn.execute(
                "SELECT * FROM users LIMIT ? OFFSET ?",
                (limit, offset)
            ).fetchall()

        conn.close()

        return jsonify([dict(user) for user in users])

    
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
    
    @app.route("/login", methods=["POST"])
    def login():

        data = request.get_json()

        name = data.get("name")
        password = data.get("password")

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE name = ?",
            (name,)
        ).fetchone()

        conn.close()

        if user is None:
            return jsonify({"error": "User not found"}), 404

        stored_password = user["password"]

        if bcrypt.checkpw(password.encode("utf-8"), stored_password):

            token = jwt.encode(
                {
                    "user_id": user["id"],
                    "role": user["role"],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
                },
                current_app.config["SECRET_KEY"],
                algorithm="HS256"
            )   

            return jsonify({
                "message": "Login successful",
                "token": token
            })

        return jsonify({"error": "Invalid password"}), 401
    
    @app.route("/profile", methods=["GET"])
    @token_required
    def profile():

        token = request.headers["Authorization"].split(" ")[1]

        data = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )

        user_id = data["user_id"]

        conn = get_db_connection()

        user = conn.execute(
            "SELECT id, name, age, role FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        conn.close()

        return jsonify(dict(user))
    
    @app.route("/admin/users", methods=["GET"])
    @admin_required
    def admin_get_users():

        conn = get_db_connection()

        users = conn.execute(
            "SELECT id, name, age, role FROM users"
        ).fetchall()

        conn.close()

        return jsonify([dict(user) for user in users])