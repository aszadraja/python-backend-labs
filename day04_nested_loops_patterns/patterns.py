"""
File: patterns.py
Day: 04
Topic: Pattern Problems
Author: Aszad Raja
Description:
    Printing simple star patterns using loops.
"""

# Status: Day 04 in progress

# Pattern 1: Square
for i in range(3):
    for j in range(3):
        print("*", end=" ")
    print()

print("----")

# Pattern 2: Right triangle
for i in range(1, 4):
    for j in range(i):
        print("*", end=" ")
    print()

if __name__ == "__main__":
    print("Patterns script executed successfully.")
