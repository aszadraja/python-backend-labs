from flask import Flask, jsonify, request
from models import init_db
from routes import register_routes
from datetime import datetime
from config import Config 
import logging

app = Flask(__name__)

app.config.from_object(Config)
# Secret key for JWT
app.config["SECRET_KEY"] = "supersecretkey"

app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success":False,
        "error":"Bad request"
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
        "success":False,
        "error": "Internal server error"
    }), 500

# Configure logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(astime)s  - %(message)s"
)

@app.before_request
def log_request():
    logging.info(
        f"{request.method} {request.path} - {datetime.utcnow()}"
    )

init_db()
register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)