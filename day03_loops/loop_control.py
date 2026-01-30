"""
File: loop_control.py
Day: 03
Topic: Loop Control Statements
Author: Aszad Raja
Description:
    Practicing break and continue.
"""

# Status: Day 03 in progress

for i in range(1, 10):
    if i == 5:
        break
    print(i)

print("----")

for i in range(1, 10):
    if i % 2 == 0:
        continue
    print(i)

if __name__ == "__main__":
    print("Loop control script executed successfully.")
