"""Validate supplied home terms, known marks and independent sale recognition.

Personal-use basis stays fixed in this profile. Taxable gains may be smaller
than economic gains only under the source-confirmed prelimited assumptions;
no legal exclusion or additional deductible cost is calculated here.
"""

from datetime import timedelta

from wealthlab.household.calendar import months


def validate_terms(scenario, holding):
    if holding.use != "personal_use_home" or not (
        holding.ownership_legal_use_and_tax_facts_supplied_confirmed
        and holding.unchanged_basis_and_no_other_asset_cashflows_confirmed
    ):
        raise ValueError(
            "Resolve home legal/use/tax facts; rental and changing-basis profiles are unsupported."
        )
    if (
        holding.provenance == "unresolved"
        or not holding.source_ref.strip()
        or not (holding.source_date <= holding.available_on <= scenario.start)
    ):
        raise ValueError("Property terms need a resolved source available at projection opening.")


def validate_debts(scenario, holding):
    debts = {d.id: d for d in scenario.debts}
    if any(key not in debts or debts[key].currency != "USD" for key in holding.linked_debt_ids):
        raise ValueError("Property liens must uniquely name existing USD household debts.")


def validate_observations(scenario, holding):
    dates = [end - timedelta(days=1) for _, end in months(scenario.start, scenario.end)]
    if [o.date for o in holding.observations] != dates:
        raise ValueError("Supply one ordered observed property value at every modeled month end.")
    if any(o.provenance == "unresolved" or o.available_on > o.date for o in holding.observations):
        raise ValueError("Property marks must be resolved and available by their own cutoff.")


def validate_sale(scenario, holding):
    sale = holding.sale
    if (holding.terminal_action == "sell") != (sale is not None):
        raise ValueError("Choose explicit retained property or a complete dated sale.")
    if sale is None:
        return
    if sale.date not in {o.date for o in holding.observations} or sale.provenance == "unresolved":
        raise ValueError("Property sale needs a resolved observed month-end closing date.")
    if sale.federal_character == "unconfirmed" or not all(
        (
            sale.costs_due_only_on_executed_close_confirmed,
            sale.no_closing_withholding_or_other_escrow_terms_confirmed,
            sale.prelimited_tax_recognition_and_no_deduction_claims_confirmed,
        )
    ):
        raise ValueError("Resolve closing costs, withholding and independent property tax facts.")
    validate_gain(holding)


def validate_gain(holding):
    sale = holding.sale
    available = max(0, sale.gross_proceeds - sale.closing_costs)
    if sale.federal_taxable_gain > max(0, available - holding.opening_federal_basis) or (
        sale.nj_taxable_gain > max(0, available - holding.opening_nj_basis)
    ):
        raise ValueError("Supplied taxable gains cannot exceed independent net economic gains.")
