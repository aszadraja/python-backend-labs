"""
File: app.py
Day: 15
Topic: Dynamic Routing & Query Parameters
Author: Aszad Raja
Description:
    Creating dynamic routes and handling query parameters.
"""

# Status: Day 15 in progress

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def home():
    return "Backend server running!"

# URL Parameter
@app.route("/user/<name>")
def user(name):
    return jsonify({
        "message": f"Hello {name}"
    })

# Query Parameters
@app.route("/add")
def add():
    a = request.args.get("a", type=int)
    b = request.args.get("b", type=int)

    if a is None or b is None:
        return jsonify({"error": "Please provide both a and b"}), 400

    return jsonify({
        "a": a,
        "b": b,
        "sum": a + b
    })

if __name__ == "__main__":
    app.run(debug=True)