"""Spanish ordinary wage amounts retain supplied recognition and independent EUR quotes."""


def update_spain(spain, binding, owner, value):
    if spain is None:
        return
    annual, row = linked_source(spain, binding)
    if annual["person_id"] != owner or row["kind"] != "income":
        raise ValueError("Retain the Spanish wage person and ordinary receipt kind.")
    native = row["amount"]
    if native["date"] != str(binding.date) or native["currency"] != "USD":
        raise ValueError("Spain wage bindings retain the supplied USD receipt and dated EUR FX.")
    native["amount"] = str(value)


def linked_source(spain, binding):
    annuals = {a["id"]: a["case"] for a in spain["assessments"]["annuals"]}
    links = [
        r
        for r in spain["source_links"]
        if r["us_income_id"] == binding.source_id
        and annuals[r["annual_id"]]["year"] == binding.date.year
    ]
    if len(links) != 1:
        raise ValueError("A Spain wage needs one explicit native source link for its year.")
    annual = annuals[links[0]["annual_id"]]
    row = next(r for r in annual["incomes"] if r["id"] == links[0]["spanish_income_id"])
    return annual, row
