"""
File: return_functions.py
Day: 05
Topic: Functions with Return
Author: Aszad Raja
Description:
    Functions that return values instead of printing.
"""

# Status: Day 05 in progress

def multiply(a, b):
    return a * b

def is_even(num):
    return num % 2 == 0

result = multiply(4, 5)
print("Multiplication:", result)

print("Is 10 even?", is_even(10))

if __name__ == "__main__":
    print("Return functions executed successfully.")
