"""Alter one independently supplied source/contract fact without silently fixing its peers."""


def fields(data):
    context = data["tax_plan"]["cases"][0]["pr_federal"]
    return context["gain_profile"], context["sources"][-1]["income"]


def mutate(data, profile, source, change):
    if change == "missing_book":
        data["lot_plan"] = None
    elif change == "unknown_trade":
        profile["gains"][0]["sale_trade_id"] = "absent_sale"
    elif change == "partial_sale":
        data["lot_plan"]["case"]["trades"][0]["quantity"] = "200"
    elif change == "basis":
        profile["gains"][0]["facts"]["federal_cost"] = "14000"
        source["federal_amount"] = "11000"
    else:
        other_change(data, profile, change)


def other_change(data, profile, change):
    if change == "acquired":
        profile["gains"][0]["facts"]["acquired"] = "2019-01-01"
    elif change == "cost":
        profile["decree"]["annual_compliance_cost"] = None
    elif change == "expense":
        data["expenses"] = []
    else:
        profile["gains"][0]["owner_id"] = "unknown_person"
