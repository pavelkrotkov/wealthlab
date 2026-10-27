"""The ordinary age-100 example exports a report that its loaders can replay."""

from io import BytesIO

from wealthlab import country_report
from wealthlab.household import report, storage
from wealthlab.household.projection import project
from wealthlab.optimization.horizon_example import synthetic
from wealthlab.ui.uploads import read


def test_default_age_100_full_report_can_be_imported_and_reprojected(tmp_path):
    scenario = synthetic().household
    rows = project(scenario)
    encoded = report.encode(report.payload(scenario, rows)).encode()
    assert 2_000_000 < len(encoded) < storage.MAX_BYTES
    assert storage.loads(read(BytesIO(encoded))) == scenario
    assert country_report.loads(encoded) == scenario
    path = tmp_path / "synthetic-age-100.json"
    path.write_bytes(encoded)
    restored = report.read_scenario(path)
    assert restored == scenario
    assert project(restored) == rows
