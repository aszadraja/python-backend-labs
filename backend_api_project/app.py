from flask import Flask, request
from flask import Flask, jsonify
from models import init_db
from routes import register_routes

app = Flask(__name__)

import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

@app.before_request
def log_request():
    logging.info(
        f"{request.method} {request.path} - {datetime.utcnow()}"
    )
# Secret key for JWT
app.config["SECRET_KEY"] = "supersecretkey"


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