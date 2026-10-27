"""Run policies on the same realized batch; never optimize with future path knowledge."""

from wealthlab.markets.country_projection import path as project_path
from wealthlab.markets.employment_compile import audit
from wealthlab.markets.household_compile import compile_marks
from wealthlab.markets.household_report import aggregate, summarize
from wealthlab.markets.household_validation import validate, validate_batch
from wealthlab.markets.medical_inflation import audit as medical_audit


def run(scenario, batch, binding, indices=None, progress=None, *, country=None):
    validate_batch(scenario, batch)
    indices = list(range(len(batch.mark_returns))) if indices is None else list(indices)
    if not indices or len(indices) != len(set(indices)):
        raise ValueError("Select unique path indices from the realized batch.")
    for index in indices:
        validate(scenario, batch, binding, index)
    outcomes, details = [], []
    for index in indices:
        case = compile_marks(scenario, batch, binding, index)
        rows, country_audit = project_path(case, batch, binding, index, country)
        outcomes.append(summarize(case, rows, index))
        details.append(
            dict(
                path=index,
                **country_audit,
                rows=rows,
                employment_changes=audit(case, binding),
                medical_bill_indexing=medical_audit(scenario, case, binding),
            )
        )
        if progress is not None:
            progress(len(outcomes), len(indices))
    return dict(
        batch_id=batch.metadata["batch_id"],
        indices=indices,
        household=scenario.model_dump(mode="json"),
        country_context=country.model_dump(mode="json") if country is not None else None,
        binding=binding.model_dump(mode="json"),
        aggregate=aggregate(scenario, batch, outcomes),
        outcomes=outcomes,
        details=details,
    )


def paired(left, right):
    if (left["batch_id"], left["indices"]) != (right["batch_id"], right["indices"]):
        raise ValueError("Paired household comparisons require the same batch and path indices.")
    return [
        dict(
            path=a["path"],
            funded_change=int(b["funded"]) - int(a["funded"]),
            reported_tax_liability_change=b["reported_tax_liability"] - a["reported_tax_liability"],
            net_cash_taxes_paid_change=b["net_cash_taxes_paid"] - a["net_cash_taxes_paid"],
            joint_feasible_change=int(b["joint_feasible"]) - int(a["joint_feasible"]),
            rebalance_commissions_change=b["rebalance_commissions"] - a["rebalance_commissions"],
            real_wealth_change=b["ending_real_wealth"] - a["ending_real_wealth"],
            discretionary_reduction_change=b["discretionary_spending_reduction"]
            - a["discretionary_spending_reduction"],
            shortfall_change=b["funding_shortfall"] - a["funding_shortfall"],
        )
        for a, b in zip(left["outcomes"], right["outcomes"], strict=True)
    ]
