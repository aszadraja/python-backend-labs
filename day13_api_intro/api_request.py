"""
File: api_request.py
Day: 13
Topic: API Requests & JSON
Author: Aszad Raja
Description:
    Making HTTP requests and reading JSON responses.
"""

# Status: Day 13 in progress

import requests

url = "https://api.github.com"

response = requests.get(url)

print("Status:", response.status_code)

data = response.json()
print("Keys:", data.keys())

if __name__ == "__main__":
    print("API intro executed successfully.")
