# Local release verification

[Issue #19](https://github.com/pavelkrotkov/wealthlab/issues/19) records final release acceptance. These dated checks distinguish source revisions and demonstrate synthetic workflows; they do not validate personal inputs or unrestricted tax profiles.

## Mac workflow checkpoint — October 27, 2026

At clean source `bfca1d6de0cd178ce3022cebbea76de8c7ec32fe`, the documented launcher started the installed application on loopback. In a real browser, keyboard activation submitted the synthetic household form. The app saved a new input file in the selected private directory; the CLI projected that file and reproduced the resulting report with byte-equivalent decoded content, including all monthly rows and provenance.

The browser imported that projection report and recalculated $224,000 ending nominal wealth. Editing the synthetic monthly income from $10,000 to $11,000 produced $236,000 and a $12,000 baseline difference. Saving that clone and comparing both private files through the CLI produced the same values. This simple synthetic case explicitly omits taxes; it checks application/file parity, not after-tax retirement safety. No private household facts were used.

The UI's saved inputs, CLI reports, comparison and screenshot evidence remain in the selected private archive, outside the public repository. New-file saves were used throughout; existing files were not overwritten. Report import validates source inputs and recalculates outcomes.

## Full-horizon optimization and combined UI

The real browser evaluated both retirement choices through 2077 under the age-100, 95% success and two-year-reserve defaults. Early retirement failed its reserve target; `candidate_1` (later retirement) was selected and passed all eight held-out paths. Its displayed 95% Wilson interval was approximately 0.6756–1.0. The four training/eight validation paths are deliberately a small execution example, not reliable evidence of personal retirement safety.

At clean `f29257c61fe9db16686e9025e3ee87c515dc59cd`, the CLI loaded the actual browser-form inputs and selected the same policy with the same held-out result. Its **46,300,060-byte audit** was then used as input to a fresh CLI optimization. The complete decoded reports were identical, including every realized path, outcome and source/dependency record. The shared 200 MB limit admits that normal full-horizon report; it does not guarantee that every larger user-selected grid fits.

The combined property/country build `edebba6d0a92a12544ad2a5b8cceb5f1df402a4c` was also launched on this Mac. The real UI showed the household form above collapsed synthetic examples and the 200 MB import capacity. Native country execution showed separate New Jersey, Puerto Rico and federal assessed/paid rows, payment currency, refunds, fees and status. The fixed-PR optimizer evaluated both retirement choices and correctly refused an age-100 safety conclusion from its short horizon.

The real fixed-home UI also evaluated both choices and withheld a safety conclusion from the short horizon. It uses the existing native close, lien and tax engine. Its retained financial/UI regression independently checks closing costs, mortgage interest, NJ tax and retained/blocked property; those contexts cannot rank as completed-exit cash. Property and country implementations passed independent exact-commit Sol 6.1 review and full required CI before merging in PRs #177 and #178. The report, layout and jurisdiction-summary stack passed the same gates in PRs #173–175 and #179.

## Reproducibility, privacy and quality

Only original synthetic cases were used. The tracked data files are the synthetic starter and attributed Spanish rule-region data; no household archive, broker export or adviser media was imported into git. Current-tree and historical searches found no selected private-archive paths, private-key markers, matching credential literals or tracked CSV/PDF/image/audio/video source files. These checks complement the existing path, import and offline-calculation checks; no scenario-upload service or brokerage connection was added.

The existing pinned environment and CLI launcher were used on Intel macOS. Full CI also exercises the pinned optional Owl environment on Linux, dependency audit and workflow checks. CC ≤ 8, MI ≥ 50, module SLOC ≤ 300, function span ≤ 60 and coverage ≥ 85% remain unchanged, including tests and tooling. The [test audit](test-audit.md) documents deliberate removals; no deleted speculative suite was restored for release.

The final delivery PR carries guide/copy changes and this evidence record over the reviewed calculation engines. All modified local documentation links, global lint/format/type/complexity checks and the three existing engine/property/country UI checks passed locally; no new test was added for these copy changes. Required CI and independent exact-commit review remain the merge gate. Consult the [coverage matrix](model-coverage.md), [source notices](dependency-notices.md) and [private input checklist](private-input-checklist.md); unsupported tax/source/contract combinations remain explicit.
