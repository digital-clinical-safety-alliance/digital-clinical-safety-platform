import sys
from mypy import api

result1 = api.run(["/cshd/app/cshd/app/functions"])

if result1[0]:
    print("Type checking report:")
    print(result1[0])  # stdout

if result1[1]:
    print("Error report:")
    print(result1[1])  # stderr


result2 = api.run(["/cshd/app/cshd/app/views.py"])

if result2[0]:
    print("Type checking report:")
    print(result2[0])  # stdout

if result2[1]:
    print("Error report:")
    print(result2[1])  # stderr

print("Exit status 1:", result1[2])
print("Exit status 2:", result2[2])
