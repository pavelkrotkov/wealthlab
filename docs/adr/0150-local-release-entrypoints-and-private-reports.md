# ADR 0150: Local release entrypoints and private report boundaries

Status: concrete current-main release fixes for issue #19; full dependent release remains open. No new dependency. This independent layer starts from verified main 6cd0cf4 and does not claim pending optimizer/cross-border/product stacks are integrated.

## Concrete gaps and smallest shared fixes

The main workbench had a real UI engine and scenario saves but no `python -m wealthlab` CLI, despite the release agreement requirement. The installation language called Owl an optional benchmark even though its pinned tables also support production FRA/RMD calculations. The private-save guard protected only its own checkout, allowing the main checkout or a sibling linked worktree to be selected as a nominally private destination.

The thin module CLI now offers `serve`, `project` and `compare`. It calls the actual existing household projection engine. It does not implement another tax engine, optimizer, protocol server or account connection. Runtime configuration runs before numerical imports. The recommended full install retains the existing extra; a deliberately smaller core-only installation is labelled limited and discloses its missing SSA/RMD support before those profiles run. No required table adapter is removed. Native launch selects the repository's absolute app path and working directory, binds 127.0.0.1, disables usage statistics and preserves the upload bound regardless of the caller's working directory. Invalid ports fail before starting a server.

UI and CLI share a reproduction payload containing validated inputs, the existing complete monthly ledger/audits, input fingerprint, actual core versions and Git revision/dirty status. Missing Git revision remains explicit. No private source path is placed in the report. A report remains conditional on its enabled plans and is never a full-tax optimization certificate. CLI comparison requires aligned horizons and uses actual projected outcomes; it does not run the pending optimizer.

## Input, output and privacy contract

Raw scenarios and known-format projection reports use one bounded UTF-8/BOM reader. The limit counts actual bytes, not Unicode characters; numeric JSON monetary values preserve Decimal precision. Projection report import validates its embedded inputs/fingerprint and ignores archived results. A new calculation is required, so a fabricated archived wealth figure cannot become an opening fact. Schema/version migrations and arbitrarily large audit imports are not silently inferred; raw scenario saves remain available.

A shared exclusive writer retains the existing fully written/fsynced temporary-file-and-hard-link operation. The temporary file stays in the selected directory, and an existing filename or destination symlink cannot be overwritten. The selected directory must already exist. Canonical paths protect aliases, and Git's common-directory/worktree metadata protects the main checkout and every linked checkout of the same public repository. Unrecognized linked metadata fails closed. It does not search for private records or create a private directory.

Project/compare JSON stdout is an explicit local report and may contain private values. Selected-directory output is optional, atomic and exclusive; a filename alone cannot silently select stdout. CLI errors do not dump raw validation input or private paths. Numerical calculation does not call a network service; the local browser UI sends its form data to loopback. Installation/dependency retrieval and an explicitly followed external documentation link are separate actions, not scenario submission.

## Reproducible evidence and remaining gate

Checks exercise native CLI execution from another directory, actual Household UI agreement, taxed input/report re-execution, original-type audit retention, no-network selected calculations, aligned comparisons, byte/BOM/precision bounds, fingerprints, all linked-checkout aliases, exclusive UTF-8 saves and existing destination symlinks. Synthetic test metadata/output stays within the selected runtime folder. Current-Mac core installation/native launch and browser keyboard checks are recorded with the final PR evidence.

The [user guide](../local-user-guide.md), [coverage matrix](../model-coverage.md), [private-input checklist](../private-input-checklist.md) and [dependency notices](../dependency-notices.md) describe actual supported workflows and pending integration. Completing this layer does not close issue #19: all prior slices must be merged and demonstrated together, dependent optimizer/cross-border completeness must be established, and exact-head required CI plus complete independent review remain mandatory.

The shared report also records the actually installed Owl production-table version,
or explicit null in a deliberately limited core-only environment. It never
substitutes the lock file version for installed metadata: a mismatched environment
therefore remains visible when reproducing SSA/RMD calculations. Metadata-only
regressions cover mismatch and absence without mutating the installed environment.
