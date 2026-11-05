try:
    print("A")
    int("abc")
    print("B")
except ValueError:
    print("C")
print("D")
