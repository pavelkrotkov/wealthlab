# Local release verification

Final release acceptance remains open in [issue #19](https://github.com/pavelkrotkov/wealthlab/issues/19). These are executed checks, not a claim that every pending branch is on the default branch.

## Mac workflow checkpoint — October 27, 2026

At clean source `bfca1d6de0cd178ce3022cebbea76de8c7ec32fe`, the documented launcher started the installed application on loopback. In a real browser, keyboard activation submitted the synthetic household form. The app saved a new input file in the selected private directory; the CLI projected that file and reproduced the resulting report with byte-equivalent decoded content, including all monthly rows and provenance.

The browser imported that projection report and recalculated $224,000 ending nominal wealth. Editing the synthetic monthly income from $10,000 to $11,000 produced $236,000 and a $12,000 baseline difference. Saving that clone and comparing both private files through the CLI produced the same values. This simple synthetic case explicitly omits taxes; it checks application/file parity, not after-tax retirement safety. No private household facts were used.

The UI's saved inputs, CLI reports, comparison and screenshot evidence remain in the selected private archive, outside the public repository. New-file saves were used throughout; existing files were not overwritten. Report import validates source inputs and recalculates outcomes.

## Remaining integrated acceptance

Current-head CI and independent reviews, the complete country/report-capacity changes, fixed property/country optimizer contexts, jurisdiction totals, optimizer audit replay and final browser checks must be verified together before release acceptance. Detailed supported profiles remain in the [coverage matrix](model-coverage.md); known limitations are not waived by a successful synthetic run.
