"""CSV schedules replace named cases/types; contract metadata stays in the JSON study.

Imported schedules invalidate the correspondence confirmation. A human must
confirm that the supplied values match the edited flows/funding path before IRRs.
"""

import csv
from io import StringIO

from wealthlab.household.storage import MAX_BYTES, MAX_MB
from wealthlab.products.life_illustration_inputs import LifeStudy

FLOW = ("flow_id", "provenance", "kind", "amount")
VALUE = ("gross_cash_value", "gross_surrender_value", "gross_death_benefit")
COLUMNS = ("illustration_id", "record_type", "date", *FLOW, *VALUE)


def export(study):
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=COLUMNS)
    writer.writeheader()
    for case in study.illustrations:
        for flow in case.flows:
            row = flow.model_dump(mode="json")
            row["flow_id"] = row.pop("id")
            writer.writerow(dict(illustration_id=case.id, record_type="flow", **row))
        for value in case.values:
            writer.writerow(
                dict(illustration_id=case.id, record_type="value", **value.model_dump(mode="json"))
            )
    return output.getvalue()


def replace(text, study):
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError(f"Import exceeds the {MAX_MB} MB limit.")
    reader = csv.DictReader(StringIO(text.removeprefix("\ufeff")))
    if reader.fieldnames != list(COLUMNS):
        raise ValueError("Use the exported schedule CSV header without missing/extra columns.")
    data = study.model_dump(mode="json")
    cases = {case["id"]: case for case in data["illustrations"]}
    seen = set()
    for row in reader:
        apply(row, cases, seen)
    if not seen:
        raise ValueError("The schedule CSV contains no rows.")
    return LifeStudy.model_validate(data)


def validate_row(row, cases):
    if None in row or None in row.values():
        raise ValueError("CSV row has extra or missing cells.")
    identifier, kind = row["illustration_id"], row["record_type"]
    if identifier not in cases or kind not in {"flow", "value"}:
        raise ValueError("Each CSV row needs a known illustration_id and flow/value record_type.")
    unused = VALUE if kind == "flow" else FLOW
    if any(row[key] for key in unused):
        raise ValueError(
            "A flow row cannot contain values; a value row cannot contain flow fields."
        )


def apply(row, cases, seen):
    validate_row(row, cases)
    identifier, kind = row["illustration_id"], row["record_type"]
    key = "flows" if kind == "flow" else "values"
    case = cases[identifier]
    if (identifier, key) not in seen:
        case[key] = []
        seen.add((identifier, key))
    case[key].append(parse(row, kind))
    case["values_match_cashflows_and_funding_path_confirmed"] = False


def parse(row, kind):
    if kind == "value":
        return dict(date=row["date"], **{key: row[key] or None for key in VALUE})
    return dict(date=row["date"], id=row["flow_id"], **{key: row[key] for key in FLOW[1:]})
