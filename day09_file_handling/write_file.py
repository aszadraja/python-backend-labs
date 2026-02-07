"""
File: write_file.py
Day: 09
Topic: File Writing
Author: Aszad Raja
Description:
    Writing and appending data to files.
"""

# Status: Day 09 in progress

with open("output.txt", "w") as file:
    file.write("Learning backend development\n")

with open("output.txt", "a") as file:
    file.write("Consistency is power\n")

print("Data written successfully.")

if __name__ == "__main__":
    print("File write executed successfully.")
