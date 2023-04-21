import json

def currency_converter(initial_currency="gbp",target_currency="gbp", amount=1000):

    with open('register.json', 'r') as c:
        conversion_data = json.load(c)
    if initial_currency or target_currency not in conversion_data:
        return amount
    else:
        rate = conversion_data[initial_currency][target_currency]
        converted_amount = amount * rate
        converted_amount = round(converted_amount, 4)
        return converted_amount

#currency_converter("gbp","dollars",1000)
