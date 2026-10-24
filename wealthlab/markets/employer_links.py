"""Link only the account owner's existing wage path, with explicit override consent.

Existing wage paths own stream mapping and active/inactive transitions. Reuse
that state to avoid inventing a second employment book or applying a job loss
to a worker already out of work.
"""

from wealthlab.employment.validation import validate as validate_employment
from wealthlab.employment.wages import at


def validate(scenario, item, account):
    if scenario.employment_plan is None:
        raise ValueError("A linked employer trigger requires an existing wage path.")
    validate_employment(scenario)
    link = item.employment
    paths = scenario.employment_plan.paths
    path = next((p for p in paths if p.id == link.path_id), None)
    if path is None or path.owner != account.owner:
        raise ValueError("Linked wage path must belong to the employer account owner.")
    if not link.replace_future_work_changes_confirmed:
        raise ValueError("Confirm replacement of future work changes after the observed trigger.")


def active(path, when):
    return at(sorted(path.changes, key=lambda e: e.date), when, path.opening_multiplier) > 0


def unique_links(employers):
    links = [b.employment.path_id for b in employers if b.employment]
    if len(links) != len(set(links)):
        raise ValueError("An employment path can have only one employer market trigger.")
