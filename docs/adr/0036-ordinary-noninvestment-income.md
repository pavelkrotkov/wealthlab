# ADR 0036: Positive ordinary noninvestment income

Status: tax-adapter foundation for remaining retirement work in #6. The HSA nonqualified household guard remains in place until its own recognition/state adapter is complete. No new dependency.

## Explicit classification and numerical carrier

The typed federal input `ordinary_noninvestment_income` represents a supplied **positive**, taxable ordinary amount that is neither earned wages, self-employment/business income, investment income nor a retirement distribution. It participates in AGI and related income thresholds. It generates no payroll tax, QBI deduction or earned-income credit by itself. Federal and NJ classification stay independent; this field does not grant legal eligibility or infer the character of a private-fund loss. Negative business losses are not accepted through this positive field.

Tax-Calculator 6.8.5 has no general other-income input in this adapter. Its `e00800` field is formally alimony, and its current-law inclusion fraction is zero. A bare mapping would drop taxable income. We instead use it as an **explicit numerical carrier**, setting `AlimonyReceived_frac_in_AGI` to one for the exact calculation year through public `Policy.implement_reform`. No statutory alimony input is supported by the typed model; this is not a claim that the supplied income is legally alimony or a change to alimony law. Adding real alimony support would require a separate channel and classification.

The installed package source uses this scalar in `AGIIncome` and `ExpandedIncome`, with the inclusion fraction applied to AGI. This yields ordinary income without SE, QBI, pension or investment-category effects. The distinct typed field and output convention disclose that numerical implementation. All other policy parameters are unchanged. The ordinary-income adapter is part of the cached calculator's immutable setup, while all household input/calculated arrays are replaced under the existing process lock. A cached year is never advanced to another cached year. Indexed/frozen-law modes use the same dollar scaling as other income.

The annual workbench exposes the new field and its classification boundary. Household scheduled-income rules and dated tax events can use it; actual receipts remain separate from taxable recognition. Neither inclusion nor a lower tax result creates a second cash receipt. Existing HSA guards and product-allocation character restrictions are preserved.

## Evidence and checks

Checked October24,2026: official [Tax-Calculator input documentation](https://taxcalc.pslmodels.org/guide/input-vars/) identifies `e00800` as alimony; [policy documentation](https://taxcalc.pslmodels.org/guide/policy-params/) documents the inclusion parameter. Installed6.8.5 `calcfunctions.py`, `records.py` and policy data were searched for every use before choosing the carrier. The package pin, source use and classification tests must be reverified during upgrades. Package variable names alone are not authority for any particular taxable receipt's legal character.

Independent controls compare $50,000 wages plus $10,000 classified other income with $60,000 wages in 2025,2026 and2036: AGI and ordinary income tax agree while payroll remains on actual wages. Other checks cover indexed-law scaling, no earned credit/QBI/payroll from the carrier alone, no cached-household leakage, and Social Security taxability. A $250,000 wage/$30,000 interest/$50,000 other-income case retains NIIT of $1,140 and additional Medicare of $450. A full household case reconciles twelve actual $5,000 receipts to one $60,000 annual return and ending cash after actual tax, without wage withholding. The real annual form submits the field successfully. Existing cached/fresh/concurrent calculator and zero-input tax-form checks remain part of validation.

This numerical primitive does not complete nonqualified HSA distributions, investment-HSA state basis, medical-bill integration, employer matches/workplace withdrawals or the rest of #6.
