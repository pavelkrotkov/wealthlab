"""Original synthetic HSA lots demonstrate cash, separate basis and real costs."""

from wealthlab.retirement.hsa_investment_inputs import HSAInvestments


def synthetic():
    return HSAInvestments.model_validate(
        dict(
            case=case(),
            opening_prices=dict(fund=100),
            marks=[
                dict(date=when, prices=dict(fund=price))
                for when, price in (("2026-01-11", 120), ("2026-01-30", 100))
            ],
            cash_targets=[
                dict(
                    id="medical_cash_reserve",
                    provenance="illustration",
                    date="2026-12-31",
                    account_id="hsa",
                    amount=5000,
                )
            ],
            funding_sources=[
                dict(account_id="hsa", security_id="fund", selection="hifo", commission=2)
            ],
            nj_treatment="taxable_securities_no_wash_assumption",
            complete_positions_and_state_basis_confirmed=True,
            conditional_state_treatment_confirmed=True,
            no_identical_outside_trading_confirmed=True,
            fees_are_custodian_charges_confirmed=True,
            ordinary_securities_no_ubti_confirmed=True,
        )
    )


def trades():
    return [
        dict(
            id=key,
            provenance="illustration",
            date=when,
            action=action,
            account_id="hsa",
            security_id="fund",
            quantity=qty,
            price=price,
            commission=cost,
        )
        for key, when, action, qty, price, cost in (
            ("sell", "2026-01-11", "sell", 40, 120, 2),
            ("reinvest", "2026-01-30", "buy", 10, 100, 1),
        )
    ]


def fees():
    return [
        dict(
            id="custody_fee",
            provenance="illustration",
            kind="custody",
            account_ids=["hsa"],
            payment_account="hsa",
            fixed_per_period=50,
            periods=[dict(start="2026-01-01", date="2026-01-31", prices=dict(fund=100))],
        )
    ]


def case():
    return dict(
        as_of="2026-01-01",
        end="2026-12-31",
        accounts=[
            dict(
                id="hsa",
                owner="primary",
                wrapper="hsa",
                cash=100,
                provenance="illustration",
            )
        ],
        securities=[
            dict(
                id="fund",
                provenance="illustration",
                wash_group="fund",
                kind="etf",
                exposure_group="equity",
            )
        ],
        lots=[
            dict(
                id="opening",
                provenance="illustration",
                account_id="hsa",
                security_id="fund",
                acquired="2020-01-01",
                federal_holding_start="2020-01-01",
                liquid_after="2020-01-01",
                quantity=100,
                federal_basis=8000,
                nj_basis=6000,
                economic_basis=8000,
            )
        ],
        trades=trades(),
        closing_prices=dict(fund=110),
        distributions=[
            dict(
                id="dividend",
                provenance="illustration",
                security_id="fund",
                ex_date="2026-01-10",
                payment_date="2026-01-15",
                recognition_date="2026-01-10",
                per_share=1,
                federal_character="dividends",
                nj_character="dividends",
            )
        ],
        price_only_marks_confirmed=True,
        nj_wash_treatment="no_wash_assumption",
        fee_schedules=fees(),
    )
