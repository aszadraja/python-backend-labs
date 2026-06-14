from functools import wraps
from flask import request, jsonify
import jwt
from config import Config

def token_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        token = request.headers.get("Authorization")

        if not token:
            return jsonify({
                "error": "Token missing"
            }), 401

        try:
            jwt.decode(
                token,
                Config.SECRET_KEY,
                algorithms=["HS256"]
            )

        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": "Token expired"
            }), 401

        except:
            return jsonify({
                "error": "Invalid token"
            }), 401

        return f(*args, **kwargs)

    return decorated