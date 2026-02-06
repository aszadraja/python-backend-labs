"""
File: dict_functions.py
Day: 08
Topic: Functions with Dictionaries
Author: Aszad Raja
Description:
    Using functions to process dictionaries.
"""

# Status: Day 08 in progress

def get_average_age(students):
    total = 0
    for age in students.values():
        total += age
    return total / len(students)

students = {
    "Amit": 20,
    "Neha": 22,
    "Rahul": 21
}

print("Average age:", get_average_age(students))

if __name__ == "__main__":
    print("Dictionary functions executed successfully.")
