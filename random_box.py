#!/usr/bin/python3
import sys
import random

def get_options():
    options = []
    for i in range(1, 35):
        for j in range(1, 16):
            options.append("HTB Machines Retired: Page {} Box {}".format(i, j))
    for i in range(1, 10):
        for j in range(1, 16):
            options.append("HTB Sherlock Retired: Page {} Box {}".format(i, j))
    for i in range(1, 44):
        for j in range(1, 16):
            options.append("HTB Challenge Retired: Page {} Box {}".format(i, j))
    options.append("Pro labs: Mythical (can decline)")
    options.append("Pro labs: Puppet (can decline)")
    for i in range(1, 7):
        options.append("Fortress {} (can decline)".format(i))
    return options

try:
    option = sys.argv[1]
except IndexError:
    print("Usage: {} [print/rand]".format(sys.argv[0]))
    print("Choose 'print': prints output for use on wheelofnames")
    print("Choose 'rand': selects a random option")
    exit(0)

options = get_options()

if option == "print":
    for o in options:
        print(o)
elif option == "rand":
    print(random.choice(options))
else:
    print("Usage: {} [print/rand]".format(sys.argv[0]))
    print("Choose 'print': prints output for use on wheelofnames")
    print("Choose 'rand': selects a random option")
    exit(0)

print()
print("Note: You have to keep this updated, this is just to generate for \n wheelofnames.com to make it more fun :)")
print()
print("#################################################")
print("### Made with <3 and >:3 by Kaden H           ###")
print("#################################################")