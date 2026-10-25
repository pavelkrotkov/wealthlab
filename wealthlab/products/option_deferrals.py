"""A misspelled deferral reference must never silently allow a gross tax loss."""


def validate(tax, rows):
    for jurisdiction in ("federal", "nj"):
        supplied = getattr(tax, f"{jurisdiction}_deferrals")
        known = {row["id"] for row in rows if row["jurisdiction"] == jurisdiction}
        if supplied.keys() - known:
            raise ValueError("Supplied option deferral references an unmatched recognition ID.")
        if supplied and tax.straddle != "supplied_deferrals":
            raise ValueError(
                "Option deferrals require the supplied_deferrals profile."
            )
