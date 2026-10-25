"""Edit household tables and optional plans, then validate one submitted scenario.

JSON/CSV inputs stay in the selected form; no arbitrary path is loaded by this
editor. Optional plan text is parsed only after submission so partial drafts
do not become apparently validated projection inputs.
"""

import csv
import io
import json

import pandas as pd
import streamlit as st

from wealthlab.household import records, schedules
from wealthlab.household.scenario import Scenario
from wealthlab.household.storage import MAX_BYTES
from wealthlab.ui.compensation import controls as compensation_controls
from wealthlab.ui.employment import controls as employment_controls
from wealthlab.ui.household_benefits import controls as benefit_controls
from wealthlab.ui.household_education import controls as education_controls
from wealthlab.ui.household_hsa import controls as hsa_controls
from wealthlab.ui.household_ira import controls as ira_controls
from wealthlab.ui.household_life import controls as life_controls
from wealthlab.ui.household_lots import controls as lot_controls
from wealthlab.ui.household_medicare import controls as medicare_controls
from wealthlab.ui.household_options import controls as option_controls
from wealthlab.ui.household_sleeves import controls as sleeve_controls
from wealthlab.ui.household_social_work import controls as social_work_controls
from wealthlab.ui.household_workplace import controls as workplace_controls
from wealthlab.ui.settings import controls
from wealthlab.ui.tax_plan import controls as tax_controls

MODELS = dict(
    members=records.Member,
    accounts=records.Account,
    incomes=schedules.Income,
    expenses=schedules.Expense,
    debts=schedules.Debt,
    contributions=schedules.Contribution,
)


def tables(payload: dict) -> dict:
    uploads = {}
    for name, model in MODELS.items():
        with st.expander(name.title(), expanded=name in {"members", "accounts"}):
            imported = st.file_uploader(f"Import {name} CSV", type="csv", key=f"csv_{name}")
            rows = payload[name]
            if imported is not None:
                uploads[name] = imported.getvalue()
            frame = pd.DataFrame(rows, columns=list(model.model_fields))
            edited = st.data_editor(frame, num_rows="dynamic", key=f"table_{name}", width="stretch")
            payload[name] = edited.to_dict(orient="records")
    return uploads


def editor(scenario: Scenario) -> Scenario | None:
    payload = scenario.model_dump(mode="json")
    with st.form("household"):
        controls(payload)
        st.caption(
            "Amounts are monthly in the stated currency; annual growth is a decimal rate. "
            "Opening balances already include year-to-date activity. End dates are exclusive."
        )
        uploads = tables(payload)
        plans = dict(
            tax_plan=tax_controls(payload, scenario),
            social_security=benefit_controls(payload, scenario),
            social_work_plan=social_work_controls(payload, scenario),
            employment_plan=employment_controls(payload, scenario),
            compensation_plan=compensation_controls(payload, scenario),
            ira_plan=ira_controls(payload, scenario),
            medicare_plan=medicare_controls(payload, scenario),
            workplace_plan=workplace_controls(payload, scenario),
            hsa_plan=hsa_controls(payload, scenario),
            education_plan=education_controls(payload, scenario),
            lot_plan=lot_controls(payload, scenario),
            sleeve_plan=sleeve_controls(payload, scenario),
            option_plan=option_controls(payload, scenario),
            life_plan=life_controls(payload, scenario),
        )
        submitted = st.form_submit_button("Validate and project", type="primary")
    if not submitted:
        return None
    payload.update({name: optional_json(raw) for name, raw in plans.items()})
    payload["usd_per_currency"] = json.loads(payload["usd_per_currency"])
    for name, raw in uploads.items():
        if len(raw) > MAX_BYTES:
            raise ValueError("CSV import exceeds the 2 MB limit.")
        payload[name] = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    return Scenario.model_validate(payload)


def optional_json(raw):
    return None if raw is None else json.loads(raw)
