from functools import wraps
from flask import request, jsonify
from time import time
from collections import defaultdict

request_count = defaultdict(list)

RATE_LIMIT = 5
WINDOW = 60

def rate_limit(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        ip = request.remote_addr
        current_time = time()

        request_count[ip] = [
            req_time for req_time in request_count[ip]
            if current_time - req_time < WINDOW
        ]

        if len(request_count[ip]) >= RATE_LIMIT:
            return jsonify({
                "error": "Too many requests"
            }), 429

        request_count[ip].append(current_time)

        return f(*args, **kwargs)

    return decorated