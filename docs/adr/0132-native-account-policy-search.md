# Native account elections in the bounded optimizer

The optimizer now accepts the existing workplace, HSA and education household books. Choices can replace employee pretax/Roth contribution schedules, ordinary separated-plan cash withdrawals, designated Roth cash withdrawals, IRA contribution schedules, personal HSA deposits, HSA withdrawal dates/amounts, and 529 deposits. Existing IRA conversion/withdrawal choices continue unchanged. `null` preserves a schedule and `[]` clears it; each schedule has one owning dimension and any dimension can be locked.

This layer reuses the native household engine, annual limits, actual payroll, qualified receipts, source withholding, cost recovery, RMDs, liquidity locks, returns and tax reconciliation. It introduces no new tax calculation or legal eligibility inference. A missing native plan blocks a choice. Full-year profiles, unsupported special features, actual compensation limits and other native guards still apply; clearing a required plan schedule can therefore produce an explicit unsupported-candidate reason.

Opening balances, basis, Roth clocks, separation/eligibility facts, employer benefits, independent NJ assumptions and required tuition/medical spending remain shared inputs. Workplace separation dates are not silently moved by a household retirement-date choice. HSA personal-deposit choices retain every fixed direct-employer event, with employer funding before chosen personal deposits on equal dates. They cannot turn a personal transfer into new employer compensation. Other payroll benefits remain fixed.

An HSA withdrawal choice must identify an existing baseline withdrawal and preserve its account, receipt list, provenance and tax mode; only its date and amount may change. Its independent NJ taxable fraction stays attached to the same identity. Removing a withdrawal prunes only its now-unused fraction; bill tax assumptions remain. This prevents an optimizer from winning by inventing qualifying receipts or renaming a taxed withdrawal to obtain a default zero fraction.

## Actual exits and safety

After-tax exit ranking still requires every noncash account balance and taxable share position to be zero. An invested HSA additionally needs its native final audit, no residual share quantity, no investment cash or distribution receivable, and no unsettled custodian fee. Rounded zero wallet values cannot hide subcent shares or obligations. A request to withdraw does not prove the request executed. Unfilled optional deposits remain separate from required spending shortfalls.

Whole-account market factors remain economic proxies, not issuer inventories. The existing concentration constraint fails when holdings are unknown. It can be explicitly disabled by the user; the UI and result retain coverage diagnostics. Cash-only HSA treatment and supplied wrapper returns retain their native explicit assumptions. Invested HSA and workplace/529 bindings can use the existing common market paths and liquidity stresses.

## UI and validation

The Optimize workspace includes a synthetic workplace/HSA/529 starter, combinable with the existing robustness checks. Editable/imported policies and complete calculation audits use the existing UI and exports. The two-year example still fails the default age-100 horizon and does not silently waive the concentration requirement.

Independent flat-market checks reconcile $326,000 opening assets, $48,000 living spending, $6,000 tuition, $1 taxable sale commission and $1,000 workplace additional tax to $270,999 after-tax exit wealth. Prior paid medical receipts yield $10,000 HSA reimbursement without paying that historical expense again. A fully invested HSA requires a real $1 commission and releases $9,999, reducing terminal wealth to $270,998. A separate designated-Roth example recovers $9,400 federal and $9,000 NJ basis from $10,000, recognizes $600/$1,000 income and $60 additional federal age tax, and ends with $271,939. Fixed employer HSA funding adds $1,000; a personal $500 deposit merely moves existing cash.

Checks cover residual workplace/529 balances, hidden invested-HSA holdings/fees, immutable tax eligibility, missing native plans, conflicting dimensions, fixed employer benefits, independent validation and the native UI. Product-specific exits, allocation controls, employer-compensation integration and cross-border optimization remain required before issue18 is complete.
