# Show native path progress through every optimizer phase

A complete 52-year demonstration takes several minutes. The prior progress bar advanced only after a whole training candidate and reached 100% before independent validation and named checks began, making continued work appear stalled.

Reuse the existing market runner's per-path callback. The optimizer supplies a phase label and an initial zero count for each candidate, frozen-winner validation and each baseline/selected named check. The Streamlit bar explicitly displays the active phase and its completed/total paths. Candidate-level callbacks remain supported for existing callers. No projection, market sample, selection, ranking or cash calculation changes; progress is not saved in financial results.

An actual paired search verifies complete result equality with and without observation, unchanged input, all phase boundaries, per-path counts and the existing candidate callback. The native form also verifies that independent-validation updates reach the UI callback. A single path can still take time; this reports completed paths rather than inventing within-path estimates.

Validation: 35 affected financial, robustness and native UI checks pass at 96.27% combined statement/branch coverage; search, robustness and progress modules each reach 100%. The strict 1,225-file audit, Ruff, formatting and ty checks pass unchanged.
