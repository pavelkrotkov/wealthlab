"""Missing state is unknown, never a zero-position completion certificate."""

from wealthlab.employment.compensation_exit_state import from_rows as employer
from wealthlab.products.option_exit_state import from_rows as options


def test_absent_projection_or_native_snapshot_is_unknown():
    assert options([]) is None
    assert options([{}]) is None
    assert options([{"option_mark_audit": [{}]}]) is None
    assert employer([]) is None
    assert employer([{"employer_tranches": [{"tranche": "old"}]}])["old"] is None
