from flask import Flask
from models import init_db
from routes import register_routes

app = Flask(__name__)

init_db()
register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)