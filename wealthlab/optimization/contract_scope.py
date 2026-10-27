"""Native option ownership and known wash identity remain household facts.

The separate option book does not implement cross-book wash reconciliation.
Known identical ordinary/HSA securities therefore block this optimizer profile,
regardless of one path's realized gain. Role labels must map to the same actual
household member or joint owner rather than retitling an existing position.
"""


def validate(household):
    plan = household.option_plan
    if plan is None:
        return
    account = next((a for a in household.accounts if a.id == plan.account_id), None)
    owner = owner_for(household, plan.case.holdings.accounts[0].owner)
    if account is None or account.owner != owner:
        raise ValueError("Map the native option owner role to the same household owner.")
    validate_wash_groups(household, plan)


def owner_for(household, role):
    owners = {"primary": household.members[0].id, "joint": "joint"}
    if len(household.members) == 2:
        owners["spouse"] = household.members[1].id
    return owners.get(role)


def validate_wash_groups(household, plan):
    groups = {s.wash_group for s in plan.case.holdings.securities}
    books = [household.lot_plan.case] if household.lot_plan else []
    if household.hsa_plan and household.hsa_plan.investments:
        books.append(household.hsa_plan.investments.case)
    if any(groups & {s.wash_group for s in book.securities} for book in books):
        raise ValueError("Option books need distinct wash groups from linked lot/HSA books.")
