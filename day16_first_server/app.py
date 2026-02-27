"""
File: app.py
Day: 16
Topic: POST Requests & JSON Handling
Author: Aszad Raja
Description:
    Handling POST requests and JSON request bodies.
"""

# Status: Day 16 in progress

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def home():
    return "Backend server running!"

# POST route
@app.route("/create-user", methods=["POST"])
def create_user():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    name = data.get("name")
    age = data.get("age")

    if not name or not age:
        return jsonify({"error": "Missing name or age"}), 400

    return jsonify({
        "message": "User created successfully",
        "user": {
            "name": name,
            "age": age
        }
    }), 201

if __name__ == "__main__":
    app.run(debug=True)