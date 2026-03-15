import jwt
import datetime
from functools import wraps
from flask import jsonify, request, current_app
import bcrypt
from database import get_db_connection

# Token blacklist
blacklisted_tokens = set()


# -------------------------------
# Helper: Get token from header
# -------------------------------
def get_token():
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None

    parts = auth_header.split(" ")

    if len(parts) != 2:
        return None

    return parts[1]


# -------------------------------
# Token Required Decorator
# -------------------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = get_token()

        if not token:
            return jsonify({"error": "Token missing"}), 401

        if token in blacklisted_tokens:
            return jsonify({"error": "Token revoked"}), 401

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


# -------------------------------
# Admin Required Decorator
# -------------------------------
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = get_token()

        if not token:
            return jsonify({"error": "Token missing"}), 401

        if token in blacklisted_tokens:
            return jsonify({"error": "Token revoked"}), 401

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


# -------------------------------
# Routes
# -------------------------------
def register_routes(app):

    @app.route("/")
    def home():
        return "Backend API running!"

    # -------------------------------
    # CREATE USER
    # -------------------------------
    @app.route("/users", methods=["POST"])
    def create_user():

        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        name = data.get("name")
        age = data.get("age")
        password = data.get("password")
        role = data.get("role", "user")

        if not name:
            return jsonify({"error": "Name required"}), 400

        if not isinstance(age, int):
            return jsonify({"error": "Age must be integer"}), 400

        if not password:
            return jsonify({"error": "Password required"}), 400

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

    # -------------------------------
    # GET USERS (Protected)
    # -------------------------------
    @app.route("/users", methods=["GET"])
    @token_required
    def get_users():

        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 5, type=int)
        search = request.args.get("search", "", type=str)

        offset = (page - 1) * limit

        conn = get_db_connection()

        if search:
            users = conn.execute(
                "SELECT id,name,age,role FROM users WHERE name LIKE ? LIMIT ? OFFSET ?",
                (f"%{search}%", limit, offset)
            ).fetchall()
        else:
            users = conn.execute(
                "SELECT id,name,age,role FROM users LIMIT ? OFFSET ?",
                (limit, offset)
            ).fetchall()

        conn.close()

        return jsonify([dict(user) for user in users])

    # -------------------------------
    # LOGIN
    # -------------------------------
    @app.route("/login", methods=["POST"])
    def login():

        data = request.get_json()

        if not data:
            return jsonify({"error": "JSON required"}), 400

        name = data.get("name")
        password = data.get("password")

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE name = ?",
            (name,)
        ).fetchone()

        conn.close()

        if not user:
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

    # -------------------------------
    # PROFILE
    # -------------------------------
    @app.route("/profile", methods=["GET"])
    @token_required
    def profile():

        token = get_token()

        data = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )

        user_id = data["user_id"]

        conn = get_db_connection()

        user = conn.execute(
            "SELECT id,name,age,role FROM users WHERE id=?",
            (user_id,)
        ).fetchone()

        conn.close()

        return jsonify(dict(user))

    # -------------------------------
    # ADMIN USERS
    # -------------------------------
    @app.route("/admin/users", methods=["GET"])
    @admin_required
    def admin_get_users():

        conn = get_db_connection()

        users = conn.execute(
            "SELECT id,name,age,role FROM users"
        ).fetchall()

        conn.close()

        return jsonify([dict(user) for user in users])

    # -------------------------------
    # LOGOUT
    # -------------------------------
    @app.route("/logout", methods=["POST"])
    @token_required
    def logout():

        token = get_token()

        blacklisted_tokens.add(token)

        return jsonify({
            "message": "Logged out successfully"
        })