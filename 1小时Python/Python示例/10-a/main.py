with open("expenses.txt", "a", encoding="utf-8") as file:
    file.write("8\n")
with open("expenses.txt", "r", encoding="utf-8") as file:
    print(file.read().strip())
