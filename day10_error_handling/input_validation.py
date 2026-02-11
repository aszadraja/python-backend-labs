"""
File: input_validation.py
Day: 10
Topic: Input Validation
Author: Aszad Raja
Description:
    Ensuring correct user input before processing.
"""

# Status: Day 10 in progress

while True:
    try:
        age = int(input("Enter your age: "))
        if age <= 0:
            print("Age must be positive.")
            continue
        break
    except ValueError:
        print("Please enter a valid number.")

print("Your age is:", age)

if __name__ == "__main__":
    print("Input validation executed successfully.")
