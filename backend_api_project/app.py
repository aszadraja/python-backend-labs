from flask import Flask, jsonify, request
from models import init_db
from routes import register_routes

app = Flask(__name__)

# Guard: limit request body size (e.g., 1MB)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024


# -------------------------------
# Global Error Handlers
# -------------------------------
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": "Bad request"
    }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Resource not found"
    }), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


# -------------------------------
# Register app parts
# -------------------------------
init_db()
register_routes(app)


if __name__ == "__main__":
    app.run(debug=True)