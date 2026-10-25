"""Original cash capital is conserved through actual production and separate share exits."""

from drilling_market_cases import price_case

from wealthlab.products.drilling_market import compare


def test_actual_commodity_receipts_and_liquid_sale_cash_reconcile_on_the_same_batch():
    result = compare(price_case())
    drilling, reference = result["policies"].values()
    assert drilling["batch_id"] == reference["batch_id"] == result["batch"]["metadata"]["batch_id"]
    well = drilling["details"][0]["rows"]
    assert well[-1]["drilling_production_receipts"] == 990
    assert (well[-1]["drilling_exit_cash"], well[-1]["closing_cash"]) == (40790, 140790)
    shares = reference["details"][0]["rows"]
    assert shares[-1]["drilling_exit_cash"] == 120000
    assert shares[-1]["net_wealth"] + shares[-1]["annual_tax"]["total_liability"] == 220000
    assert result["full_tax_optimization_supported"] is False
