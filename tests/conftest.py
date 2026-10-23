"""Set cache paths before numerical packages are imported during collection."""

from wealthlab.runtime import configure

configure()

import pytest  # noqa: E402

from wealthlab.household.example import synthetic  # noqa: E402


@pytest.fixture
def payload():
    return synthetic().model_dump(mode="json")
