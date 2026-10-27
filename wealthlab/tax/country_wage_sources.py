"""Native wage credit sources keep person, currency and actual recognition date fixed."""


def update_credit(data, binding, owner, value):
    profiles = [
        p
        for p in data["foreign_tax_plan"]["credit_profiles"]
        if p["annual"]["policy"]["year"] == binding.date.year
    ]
    if len(profiles) != 1:
        raise ValueError("A bound wage needs one original country credit profile for its year.")
    rows = [r for r in profiles[0]["income"] if r["id"] == binding.source_id]
    if len(rows) != 1:
        raise ValueError("A bound wage needs its existing stable US source identity.")
    row = rows[0]
    if (row["owner_id"], row["kind"], row["value"]["currency"], row["value"]["date"]) != (
        owner,
        "wages",
        "USD",
        str(binding.date),
    ):
        raise ValueError("Keep wage source person, kind, currency and recognition date fixed.")
    row["value"]["amount"] = str(value)
