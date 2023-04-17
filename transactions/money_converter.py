import json

def currency_converter(initial_currency,amount=1000,target_currency="gbp"):

    with open('register.json', 'r') as c:
        conversion_data = json.load(c)
    if initial_currency or target_currency not in conversion_data:
        return amount
    else:
        rate = conversion_data[initial_currency][target_currency]
        converted_amount = amount * rate
        return converted_amount

#currency_converter("gbp", 1000, "dollars")
