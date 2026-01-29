"""
File: conditions.py
Day: 02
Topic: Conditional Statements
Author: Aszad Raja 
Description:
    Practicing if, elif, else and logical conditions.
"""

# Status: Day 02 in progress

age = int(input("Enter your age: "))

if age >= 18:
    print("You are eligible to vote.")
elif age > 0:
    print("You are not eligible to vote.")
else:
    print("Invalid age")

if age >= 18 and age < 60:
    print("Working age group")

if __name__ == "__main__":
    print("Conditions script executed successfully.")
