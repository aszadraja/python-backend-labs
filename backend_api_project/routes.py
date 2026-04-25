import os
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request, current_app
import bcrypt
import jwt
import datetime
from functools import wraps
from time import time
from collections import defaultdict
import secrets

CACHE_EXPIRE = 60
cache = {}

from database import get_db_connection

try:
    conn = get_db_connection()
    print("✅ Connected to PostgreSQL")
    conn.close()
except Exception as e:
    print("❌ Error:", e)

# -----------------------------
# DB CONNECTION (PostgreSQL)
# -----------------------------
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="mydb",
        user="postgres",
        password="kali",
        cursor_factory=RealDictCursor
    )

# -----------------------------
# Rate Limit Config
# -----------------------------
request_count = defaultdict(list)
RATE_LIMIT = 5
WINDOW = 60

blacklisted_tokens = set()

# -----------------------------
# Token Middleware
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

        request_count[ip] = [t for t in request_count[ip] if now - t < WINDOW]

        if len(request_count[ip]) >= RATE_LIMIT:
            return jsonify({"error": "Too many requests"}), 429

        request_count[ip].append(now)

        return f(*args, **kwargs)

    return decorated

# -----------------------------
# ROUTES
# -----------------------------
def register_routes(app):

    @app.route("/")
    def home():
        return "Backend API Running 🚀"

    # -----------------------------
    # CREATE USER
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

        if not isinstance(age, int):
            return jsonify({"error": "Age must be integer"}), 400

        if not password or len(password) < 6:
            return jsonify({"error": "Weak password"}), 400

        name = name.strip().lower()
        verification_token = secrets.token_hex(16)

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (name, age, password, verification_token) VALUES (%s, %s, %s, %s)",
                (name, age, hashed_password, verification_token)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            conn.close()
            return jsonify({"error": "User already exists"}), 400

        conn.close()

        return jsonify({
            "message": "User registered",
            "verification_token": verification_token
        }), 201

    # -----------------------------
    # VERIFY EMAIL
    # -----------------------------
    @app.route("/verify-email", methods=["POST"])
    def verify_email():

        token = request.json.get("token")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE verification_token=%s",
            (token,)
        )
        user = cursor.fetchone()

        if not user:
            conn.close()
            return jsonify({"error": "Invalid token"}), 400

        cursor.execute(
            "UPDATE users SET is_verified=TRUE, verification_token=NULL WHERE id=%s",
            (user["id"],)
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "Email verified successfully"})

    # -----------------------------
    # LOGIN
    # -----------------------------
    @app.route("/login", methods=["POST"])
    @rate_limit
    def login():

        data = request.get_json()
        name = data.get("name")
        password = data.get("password")

        if not name or not password:
            return jsonify({"error": "Missing credentials"}), 400

        name = name.strip().lower()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE name=%s",
            (name,)
        )
        user = cursor.fetchone()

        conn.close()

        if not user:
            return jsonify({"error": "User not found"}), 404

        if not user["is_verified"]:
            return jsonify({"error": "Email not verified"}), 403

        if not bcrypt.checkpw(
            password.encode("utf-8"),
            user["password"].encode("utf-8")
        ):
            return jsonify({"error": "Invalid password"}), 401

        access_token = jwt.encode(
            {
                "user_id": user["id"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256"
        )

        refresh_token = jwt.encode(
            {
                "user_id": user["id"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256"
        )

        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token
        })

    # -----------------------------
    # GET USERS
    # -----------------------------
    @app.route("/users", methods=["GET"])
    @token_required
    @rate_limit
    def get_users():

        cache_key = tuple(sorted(request.args.items()))
        current_time = time()

        #  Check Cache
        if cache_key in cache:
            data, timestamp = cache[cache_key]
            if current_time - timestamp < CACHE_EXPIRE:
                return jsonify({
                    "source": "cache",
                    "data": data
                })
            else:
                del cache[cache_key]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
        # Fetch form DB
            page = request.args.get("page", 1, type=int)
            limit = request.args.get("limit", 5, type=int)
            search = request.args.get("search", "")
            sort = request.args.get("sort", "id")
            order = request.args.get("order", "asc")
            offset = (page - 1) * limit

        # Sorting 
            if sort not in ["id", "name", "age"]:
                sort = "id"
        
            if order.lower() not in ["asc", "desc"]:
                order = "asc"

         # Base query
            query = "SELECT id, name, age FROM users WHERE name LIKE %s"
            params = [f"%{search}%"]

            # Add sorting and pagination
            query += f" ORDER BY {sort} {order.upper()} LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cursor.execute(query,params)
        
            columns = [col[0] for col in cursor.description]
            users = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        finally:
            conn.close()

        # Save to cache
        cache[cache_key] = (users, current_time)

        return jsonify({
            "page": page,
            "limit": limit,
            "data": users
        })

    # -----------------------------
    # UPDATE USER
    # -----------------------------
    @app.route("/users/<int:user_id>", methods=["PUT"])
    @token_required
    def update_user(user_id):

        if request.user_id != data["user_id"]:
            return jsonify({"error": "Unauthorized"}), 403

        data = request.get_json()
        name = data.get("name")
        age = data.get("age")

        if not name or not isinstance(age, int):
            return jsonify({"error": "Invalid input"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET name=%s, age=%s WHERE id=%s",
            (name.strip().lower(), age, user_id)
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "User updated"})

    # -----------------------------
    # LOGOUT
    # -----------------------------
    @app.route("/logout", methods=["POST"])
    @token_required
    def logout():

        token = request.headers["Authorization"].split(" ")[1]
        blacklisted_tokens.add(token)

        return jsonify({"message": "Logged out"})

    # -----------------------------
    # PROFILE
    # -----------------------------
    @app.route("/profile", methods=["GET"])
    @token_required
    def profile():

        user_id = request.user_id

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, name, age, role, profile_image FROM users WHERE id=%s",
            (user_id,)
        )
        user = cursor.fetchone()

        conn.close()

        return jsonify(user)

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":

    app = Flask(__name__)

    app.config["SECRET_KEY"] = "super_secret_key"

    register_routes(app)

    app.run(debug=True)