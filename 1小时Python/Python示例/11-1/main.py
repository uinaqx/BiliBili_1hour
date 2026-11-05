text = input()
try:
    amount = int(text)
    print(amount)
except ValueError:
    print("not an integer")
print("done")
