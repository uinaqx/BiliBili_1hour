prices = {"tea": 8, "bread": 12}
prices["tea"] = 10
prices["milk"] = 6
del prices["bread"]
print(prices["tea"], prices["milk"])
print(len(prices))
