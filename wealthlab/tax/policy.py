"""Keep published-year evaluation separate from explicitly hypothetical future law."""

from typing import Literal

from pydantic import Field

from wealthlab.tax.facts import TaxModel


class TaxPolicy(TaxModel):
    year: int = Field(ge=2025, le=2145)
    mode: Literal["package_law", "freeze_2025", "index_2025"]
    annual_index: float = Field(ge=-0.05, le=0.2)

    def valuation(self) -> tuple[int, float, str]:
        if self.mode == "package_law":
            if self.year > 2036:
                raise ValueError(
                    "Installed package law ends in 2036; choose an explicit future assumption."
                )
            return self.year, 1.0, f"Tax-Calculator 6.8.5 parameters for {self.year}"
        factor = (1 + self.annual_index) ** (self.year - 2025) if self.mode == "index_2025" else 1.0
        label = (
            f"Hypothetical {self.mode}: 2025 law with all dollar parameters scaled by {factor:.6f}"
        )
        return 2025, factor, label
