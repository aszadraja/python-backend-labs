"""
File: basics.py
Day: 01
Topic: Python Basics
Author: Cys Cyber
Description:
    Practicing variables, data types, and basic input/output.
"""

# Status: Day 01 completed

name = input("Enter your name: ")
age = int(input("Enter your age: "))

print("Hello", name)
print("You will be", age + 1, "next year")

a = 10
b = 5.5
c = "Python"
d = True

print(type(a), type(b), type(c), type(d))

if __name__ == "__main__":
    print("Day 01 execution completed successfully.")
