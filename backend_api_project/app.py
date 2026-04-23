from flask import Flask, jsonify, request
from models import init_db
from routes import register_routes
from config import Config
from datetime import datetime
from flasgger import Swagger
import logging

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.config.from_object(Config)
Swagger(app)

# Secret key for JWT
app.config["SECRET_KEY"] = "supersecretkey"
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "error": "Bad request"}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"success": False, "error": "Internal server error"}), 500

# Logging fix
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"   # ✅ FIXED
)

@app.before_request
def log_request():
    logging.info(f"{request.method} {request.path} - {datetime.utcnow()}")

# Initialize DB and routes
init_db()
register_routes(app)

# Run locally only
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)