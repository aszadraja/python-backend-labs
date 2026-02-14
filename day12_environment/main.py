"""
File: main.py
Day: 12
Topic: Virtual Environment & Packages
Author: Aszad Raja
Description:
    Using installed libraries inside isolated environment.
"""

# Status: Day 12 in progress

import requests

response = requests.get("https://api.github.com")

print("Status Code:", response.status_code)

if __name__ == "__main__":
    print("Environment test executed successfully.")
