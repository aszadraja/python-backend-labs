"""
File: dict_basics.py
Day: 07
Topic: Dictionaries - Basics
Author: Aszad Raja
Description:
    Practicing dictionary creation, access, and iteration.
"""

# Status: Day 07 in progress

student = {
    "name": "Aszad Raja",
    "age": 21,
    "course": "CSE"
}

print("Name:", student["name"])

student["age"] = 22
student["college"] = "XYZ University"

for key, value in student.items():
    print(key, ":", value)

if __name__ == "__main__":
    print("Dictionary basics executed successfully.")
