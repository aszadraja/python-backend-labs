"""
File: app.py
Day: 17
Topic: CRUD Operations in Flask
Author: Aszad Raja
Description:
    Implementing full CRUD operations using in-memory storage.
"""

# Status: Day 17 in progress

from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory database
users = []

@app.route("/")
def home():
    return "CRUD API running!"

# CREATE (POST)
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    if not data or "name" not in data or "age" not in data:
        return jsonify({"error": "Invalid input"}), 400

    users.append(data)
    return jsonify({"message": "User added", "users": users}), 201

# READ (GET)
@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(users)

# UPDATE (PUT)
@app.route("/users/<int:index>", methods=["PUT"])
def update_user(index):
    if index >= len(users):
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    users[index] = data
    return jsonify({"message": "User updated", "users": users})

# DELETE (DELETE)
@app.route("/users/<int:index>", methods=["DELETE"])
def delete_user(index):
    if index >= len(users):
        return jsonify({"error": "User not found"}), 404

    deleted = users.pop(index)
    return jsonify({"message": "User deleted", "deleted": deleted})

if __name__ == "__main__":
    app.run(debug=True)