"""
File: basic_functions.py
Day: 05
Topic: Functions - Basics
Author: Aszad Raja
Description:
    Defining and calling simple functions with parameters.
"""

# Status: Day 05 in progress

def greet_user(name):
    print(f"Hello, {name}!")

def add_numbers(a, b):
    print("Sum:", a + b)

greet_user("Aszad")
add_numbers(5, 10)

if __name__ == "__main__":
    print("Basic functions executed successfully.")
