"""
File: main.py
Day: 11
Topic: Using modules
Author: Aszad Raja
Description:
    Importing and using functions from another file.
"""

# Status: Day 11 in progress

import utils

print("Addition:", utils.add(5, 3))
print("Is 10 even?", utils.is_even(10))

if __name__ == "__main__":
    print("Module execution successful.")
