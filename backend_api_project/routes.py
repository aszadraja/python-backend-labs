from flask import Flask, jsonify, request, current_app
from database import get_db_connection
import bcrypt
import jwt
import datetime
from functools import wraps
from time import time

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
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return jsonify({"error": "Token Missing"}), 401

        if token in blacklisted_tokens:
            return jsonify({"error": "Token has been revoked"}), 401

        try:
            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
                leeway=5   # prevent seconds delay issue
            )
            print("Decoded:", data)
            print("Current:", int(time()))

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

        ip = request.remote_addr
        now = time()

        if ip not in request_count:
            request_count[ip] = []

        request_count[ip] = [
            t for t in request_count[ip]
            if now - t < WINDOW
        ]

        if len(request_count[ip]) >= RATE_LIMIT:
            return jsonify({
                "error": "Too many requests"
            }), 429

        request_count[ip].append(now)

        return f(*args, **kwargs)

    return decorated


# -----------------------------
# Routes
# -----------------------------
def register_routes(app):

    @app.route("/")
    def home():
        return "Backend API Running"


    # -----------------------------
    # Create User
    # -----------------------------
    @app.route("/users", methods=["POST"])
    @rate_limit
    def create_user():

        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid input"}), 400

        name = data.get("name").strip().lower()
        age = data.get("age")
        password = data.get("password")

        if not name:
            return jsonify({"error": "Name required"}), 400

        if not isinstance(age, int):
            return jsonify({"error": "Age must be integer"}), 400

        if not password:
            return jsonify({"error": "Password required"}), 400

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        conn = get_db_connection()

        conn.execute(
            "INSERT INTO users (name, age, password) VALUES (?, ?, ?)",
            (name, age, hashed_password)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "User created"
        })


    # -----------------------------
    # Login
    # -----------------------------
    @app.route("/login", methods=["POST"])
    @rate_limit
    def login():

        data = request.get_json()

        name = data.get("name").strip().lower()
        password = data.get("password")

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE name=?",
            (name,)
        ).fetchone()

        conn.close()

        if not user:
            return jsonify({"error": "User not found"}), 404

        if bcrypt.checkpw(
            password.encode("utf-8"),
            user["password"].encode("utf-8")
        ):

            access_token = jwt.encode(
                {
                    "user_id": user["id"],
                    #"role": user["role"],
                    "exp": datetime.datetime.utcnow()
                    + datetime.timedelta(
                        minutes=current_app.config["ACCESS_TOKEN_EXPIRE"]
                    )
                },
                current_app.config["SECRET_KEY"],
                algorithm="HS256"
            )

            refresh_token = jwt.encode(
                {
                    "user_id": user["id"],
                    "exp": datetime.datetime.utcnow()
                    + datetime.timedelta(
                        days=current_app.config["REFRESH_TOKEN_EXPIRE"]
                    )
                },
                current_app.config["SECRET_KEY"],
                algorithm="HS256"
            )

            return jsonify({
                "access_token": access_token,
                "refresh_token": refresh_token
            })

        return jsonify({"error": "Invalid password"}), 401


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
            "SELECT * FROM users LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()

        conn.close()

        return jsonify({
            "success": True,
            "data": [dict(user) for user in users]
        })
    
    # -----------------------------
    # Refresh Route
    # -----------------------------
    @app.route("/refresh", methods=["POST"])
    def refresh():
        data = request.get_json()
        refresh_token = data.get("refresh_token")

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
                    + datetime.timedelta(
                        minutes=current_app.config["ACCESS_TOKEN_EXPIRE"]
                    )
                },
                current_app.config["SECRET_KEY"],
                algorithm="HS256"
            )

            return jsonify({
                "access_token": access_token
            })
        
        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": "Refresh token expired"
            }), 401
        
        except jwt.InvalidTokenError:
            return jsonify({
                "error": "Invalid Token error"
            }), 401

    # -----------------------------
    # Update User
    # -----------------------------
    @app.route("/users/<int:user_id>", methods=["PUT"])
    @token_required
    def update_user(user_id):

        data = request.get_json()

        name = data.get("name").strip().lower()
        age = data.get("age")

        conn = get_db_connection()

        conn.execute(
            "UPDATE users SET name=?, age=? WHERE id=?",
            (name, age, user_id)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "message": "User updated"
        })


    # -----------------------------
    # Delete Users
    # -----------------------------
    @app.route("/users", methods=["DELETE"])
    @token_required
    def delete_users():

        conn = get_db_connection()

        conn.execute("DELETE FROM users")

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Users deleted"
        })


    # -----------------------------
    # Logout
    # -----------------------------
    @app.route("/logout", methods=["POST"])
    @token_required
    def logout():

        token = request.headers["Authorization"].split(" ")[1]

        blacklisted_tokens.add(token)

        return jsonify({
            "message": "Logged out successfully"
        })


# -----------------------------
# Main App
# -----------------------------
if __name__ == "__main__":

    app = Flask(__name__)

    app.config["SECRET_KEY"] = "super_secret_key"
    app.config["JWT_EXPIRATION"] = 60   # seconds

    register_routes(app)

    app.run(debug=True)