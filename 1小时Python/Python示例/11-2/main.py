def require_amount(amount):
    if amount < 0:
        raise ValueError("negative amount")
    return amount
try:
    print(require_amount(-5))
except ValueError as error:
    print(error)
