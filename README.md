# Wealthlab

A local-first financial scenario workbench. **Planning stage; no projection engine is shipped yet.**

The intended workflow is to define a household, compare explicit policies under the same market paths, inspect spending shortfalls and taxes, and explore better policies within user-set bounds.

- [Scope and glossary](CONTEXT.md)
- [Software reuse research](docs/software-research.md)
- [Implementation tickets, dependencies and acceptance checks](docs/implementation-plan.md)
- [Architecture decisions](docs/adr/0001-local-scenario-workbench.md)

The public repository contains code, public-source references and synthetic fixtures only. Household records, account exports, credentials and private illustrations stay outside version control. No brokerage trading or account connection is planned for the first complete version.

## Delivery standard

Every feature must work through the UI and calculation engine, expose its assumptions, include a reproducible check, and pass code quality and review. An unsupported tax rule or missing product term must be visible; it must not silently become a zero tax rate or guaranteed return.
