"""
File: strings.py
Day: 02
Topic: String Basics
Author: Cys Cyber
Description:
    Practicing common string operations.
"""

# Status: Day 02 in progress

text = "Python Backend Developer"

print(text.lower())
print(text.upper())
print(text.replace("Backend", "API"))
print(text.split())

if "Python" in text:
    print("Python found in text")

if __name__ == "__main__":
    print("Strings script executed successfully.")
