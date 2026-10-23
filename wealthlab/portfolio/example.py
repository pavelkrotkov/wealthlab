"""Independent synthetic holdings, never inferred private holdings or tax eligibility."""

from wealthlab.portfolio.cases import LotCase


def synthetic() -> LotCase:
    return LotCase.model_validate(
        dict(
            as_of="2026-01-01",
            end="2026-12-31",
            accounts=[
                dict(
                    id="brokerage",
                    provenance="assumption",
                    owner="joint",
                    wrapper="taxable",
                    cash="1000",
                )
            ],
            securities=[
                dict(
                    id="STOCK",
                    provenance="assumption",
                    wash_group="STOCK",
                    kind="stock",
                    exposure_group="company",
                )
            ],
            lots=[
                dict(
                    id="original",
                    provenance="assumption",
                    account_id="brokerage",
                    security_id="STOCK",
                    acquired="2020-01-01",
                    federal_holding_start="2020-01-01",
                    liquid_after="2020-01-01",
                    quantity="100",
                    federal_basis="5000",
                    nj_basis="6000",
                )
            ],
            trades=[
                dict(
                    id="sale",
                    provenance="assumption",
                    date="2026-06-01",
                    action="sell",
                    account_id="brokerage",
                    security_id="STOCK",
                    quantity="25",
                    price="100",
                    commission="5",
                    selection="fifo",
                )
            ],
            closing_prices={"STOCK": "100"},
        )
    )
