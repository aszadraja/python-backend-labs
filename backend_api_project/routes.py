import os
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request, current_app
from database import get_db_connection
import bcrypt
import jwt
import datetime
from functools import wraps
from time import time
import secrets

request_count = {}
RATE_LIMIT = 5
WINDOW = 60

blacklisted_tokens = set()

# -----------------------------
# Token Required Middleware
# -----------------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if "Authorization" in request.headers:
            try:
                token = request.headers["Authorization"].split(" ")[1]
            except IndexError:
                return jsonify({"error": "Invalid token format"}), 401

        if not token:
            return jsonify({"error": "Token Missing"}), 401

        if token in blacklisted_tokens:
            return jsonify({"error": "Token revoked"}), 401

        try:
            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
                leeway=5
            )

            request.user_id = data["user_id"]

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401

        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated


# -----------------------------
# Rate Limit Middleware
# -----------------------------
def rate_limit(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        now = time()

        if ip not in request_count:
            request_count[ip] = []

        request_count[ip] = [t for t in request_count[ip] if now - t < WINDOW]

        if len(request_count[ip]) >= RATE_LIMIT:
            return jsonify({"error": "Too many requests"}), 429

        request_count[ip].append(now)

        return f(*args, **kwargs)

    return decorated


# -----------------------------
# Routes
# -----------------------------
def register_routes(app):

    @app.route("/")
    def home():
        return "Backend API Running 🚀"

    # -----------------------------
    # Create User
    # -----------------------------
    @app.route("/users", methods=["POST"])
    @rate_limit
    def create_user():

        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid input"}), 400

        name = data.get("name")
        age = data.get("age")
        password = data.get("password")

        if not name:
            return jsonify({"error": "Name required"}), 400

        name = name.strip().lower()

        if not isinstance(age, int):
            return jsonify({"error": "Age must be integer"}), 400

        if not password or len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        conn = get_db_connection()

        try:
            conn.execute(
                "INSERT INTO users (name, age, password) VALUES (?, ?, ?)",
                (name, age, hashed_password)
            )
            conn.commit()
        except Exception:
            conn.close()
            return jsonify({"error": "User already exists"}), 400

        conn.close()

        return jsonify({"message": "User created"}), 201

    # -----------------------------
    # Login
    # -----------------------------
    @app.route("/login", methods=["POST"])
    @rate_limit
    def login():

        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid input"}), 400

        name = data.get("name")
        password = data.get("password")

        if not name or not password:
            return jsonify({"error": "Missing credentials"}), 400

        name = name.strip().lower()

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE name=?",
            (name,)
        ).fetchone()

        conn.close()

        if not user:
            return jsonify({"error": "User not found"}), 404

        if not bcrypt.checkpw(
            password.encode("utf-8"),
            user["password"].encode("utf-8")
        ):
            return jsonify({"error": "Invalid password"}), 401

        access_token = jwt.encode(
            {
                "user_id": user["id"],
                "exp": datetime.datetime.utcnow()
                + datetime.timedelta(minutes=current_app.config["ACCESS_TOKEN_EXPIRE"])
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256"
        )

        refresh_token = jwt.encode(
            {
                "user_id": user["id"],
                "exp": datetime.datetime.utcnow()
                + datetime.timedelta(days=current_app.config["REFRESH_TOKEN_EXPIRE"])
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256"
        )

        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token
        })

    # -----------------------------
    # Get Users
    # -----------------------------
    @app.route("/users", methods=["GET"])
    @token_required
    @rate_limit
    def get_users():

        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 5, type=int)

        offset = (page - 1) * limit

        conn = get_db_connection()

        users = conn.execute(
            "SELECT id, name, age FROM users LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()

        conn.close()

        return jsonify({
            "page": page,
            "limit": limit,
            "data": [dict(user) for user in users]
        })

    # -----------------------------
    # Refresh Token
    # -----------------------------
    @app.route("/refresh", methods=["POST"])
    def refresh():

        data = request.get_json()
        refresh_token = data.get("refresh_token")

        if not refresh_token:
            return jsonify({"error": "Missing refresh token"}), 400

        try:
            decoded = jwt.decode(
                refresh_token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            access_token = jwt.encode(
                {
                    "user_id": decoded["user_id"],
                    "exp": datetime.datetime.utcnow()
                    + datetime.timedelta(minutes=current_app.config["ACCESS_TOKEN_EXPIRE"])
                },
                current_app.config["SECRET_KEY"],
                algorithm="HS256"
            )

            return jsonify({"access_token": access_token})

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Refresh token expired"}), 401

        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid refresh token"}), 401

    # -----------------------------
    # Update User
    # -----------------------------
    @app.route("/users/<int:user_id>", methods=["PUT"])
    @token_required
    def update_user(user_id):

        if request.user_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        data = request.get_json()

        name = data.get("name")
        age = data.get("age")

        if not name or not isinstance(age, int):
            return jsonify({"error": "Invalid input"}), 400

        name = name.strip().lower()

        conn = get_db_connection()

        conn.execute(
            "UPDATE users SET name=?, age=? WHERE id=?",
            (name, age, user_id)
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "User updated"})

    # -----------------------------
    # Delete Users (DISABLED)
    # -----------------------------
    @app.route("/users", methods=["DELETE"])
    @token_required
    def delete_users():
        return jsonify({"error": "Not allowed"}), 403

    # -----------------------------
    # Logout
    # -----------------------------
    @app.route("/logout", methods=["POST"])
    @token_required
    def logout():

        token = request.headers["Authorization"].split(" ")[1]
        blacklisted_tokens.add(token)

        return jsonify({"message": "Logged out successfully"})

    # -----------------------------
    # Forgot Password
    # -----------------------------
    @app.route("/forgot-password", methods=["POST"])
    @rate_limit
    def forgot_password():

        data = request.get_json()
        name = data.get("name")

        if not name:
            return jsonify({"error": "Name required"}), 400

        name = name.strip().lower()

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE name=?",
            (name,)
        ).fetchone()

        if not user:
            conn.close()
            return jsonify({"error": "User not found"}), 404

        reset_token = secrets.token_hex(16)

        conn.execute(
            "UPDATE users SET reset_token=? WHERE id=?",
            (reset_token, user["id"])
        )

        conn.commit()
        conn.close()

        print(f"Reset token: {reset_token}")  # simulate email

        return jsonify({
            "message": "Reset token generated",
            "reset_token": reset_token
        })

    # -----------------------------
    # Reset Password
    # -----------------------------
    @app.route("/reset-password", methods=["POST"])
    @rate_limit
    def reset_password():

        data = request.get_json() or {}

        token = data.get("token")
        new_password = data.get("password")

        if not token or not new_password:
            return jsonify({"error": "Invalid input"}), 400

        if len(new_password) < 6:
            return jsonify({"error": "Weak password"}), 400

        hashed_password = bcrypt.hashpw(
            new_password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        conn = get_db_connection()

        print("Received Token:", token)

        user = conn.execute(
            "SELECT * FROM users WHERE reset_token=?",
            (token,)
        ).fetchone()

        print("User Found:", user)

        if not user:
            conn.close()
            return jsonify({"error": "Invalid token"}), 400

        conn.execute(
            "UPDATE users SET password=?, reset_token=? WHERE id=?",
            (hashed_password, None, user["id"])
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "Password reset successful"})

    #-------------------------
    #Upload Profile Image Route
    #-------------------------
    @app.route("/upload-profile", methods=["POST"])
    @token_required
    def upload_profile():

        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["files"]

        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400
        
        filename = secure_filename(file.filename)

        upload_path = os.path.join("uploads", filename)

        file.save(upload_path)

        token = request.headers["Authorization"].split(" ")[1]

        decoded = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )

        user_id = decoded["user_id"]

        conn = get_db_connection()

        conn.execute(
            "UPDATE users SET profile_image = ? WHERE id = ?",
            (upload_path, user_id)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Profile image uploaded",
            "file": upload_path
        })
    
    #--------------------------
    # Get Profile Route
    #--------------------------
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
            "SELECT id, name, age, role, profile_image FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        conn.close()

        return jsonify(dict(user))
# -----------------------------
# Main App
# -----------------------------
if __name__ == "__main__":

    app = Flask(__name__)

    app.config["SECRET_KEY"] = "super_secret_key"
    app.config["ACCESS_TOKEN_EXPIRE"] = 15
    app.config["REFRESH_TOKEN_EXPIRE"] = 7

    register_routes(app)

    app.run(debug=True)