"""
File: app.py
Day: 14
Topic: First Flask Server
Author: Aszad Raja
Description:
    Creating basic API routes.
"""

# Status: Day 14 in progress

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to my backend server!"

@app.route("/user")
def user():
    data = {
        "name": "Cys",
        "role": "Backend Learner"
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
