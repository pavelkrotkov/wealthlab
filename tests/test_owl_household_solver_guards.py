"""An optional reference must fail visibly when upstream axes or policy scope drift."""

from types import SimpleNamespace

import numpy as np
import pytest

from wealthlab.retirement.owl_household_inputs import synthetic
from wealthlab.retirement.owl_household_solver import validate


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"year_n": np.array([2000, 2001, 2002])}, "years differ"),
        ({"w_ijn": np.zeros((2, 4, 3))}, "account axes"),
        ({"T_n": np.array([0, np.nan, 0])}, "nonfinite"),
        ({"x_in": np.ones((1, 3))}, "locks conversions"),
        ({"st_T_n": np.ones(3)}, "omits state taxes"),
    ],
)
def test_upstream_contract_is_checked(changes, message):
    case = synthetic()
    data = dict(
        year_n=np.arange(case.start_year, case.start_year + 3),
        w_ijn=np.zeros((1, 4, 3)),
        b_ijn=np.zeros((1, 4, 4)),
        g_n=np.zeros(3),
        T_n=np.zeros(3),
        st_T_n=np.zeros(3),
        x_in=np.zeros((1, 3)),
        sigmaBar_n=np.zeros(3),
        MAGI_n=np.zeros(3),
        gamma_n=np.ones(4),
    )
    with pytest.raises(ValueError, match=message):
        validate(SimpleNamespace(**dict(data, **changes)), case)
