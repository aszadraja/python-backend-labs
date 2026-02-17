"""
File: list_functions.py
Day: 08
Topic: Functions with Lists
Author: Aszad Raja
Description:
    Using functions to process lists.
"""

# Status: Day 08 in progress

def find_max(numbers):
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val

def count_even(numbers):
    count = 0
    for num in numbers:
        if num % 2 == 0:
            count += 1
    return count

def count_odd(numbers):
    count = 0
    for num in numbers:
        if num %2 != 0:
            count +=1
    return count
    
def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

def find_primes(numbers):
    primes = []
    for num in numbers:
        if is_prime(num):
            primes.append(num)
    return primes

nums = [3, 7, 2, 9, 4]

print("Max:", find_max(nums))
print("Even count:", count_even(nums))
print("Odd count:", count_odd(nums))
print("Prime count:", find_primes(nums))


if __name__ == "__main__":
    print("List functions executed successfully.")
