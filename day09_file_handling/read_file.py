"""
File: read_file.py
Day: 09
Topic: File Reading
Author: Aszad Raja
Description:
    Reading file content and processing lines.
"""

# Status: Day 09 in progress

with open("sample.txt", "r") as file:
    for line in file:
        print(line.strip())

if __name__ == "__main__":
    print("File read executed successfully.")
