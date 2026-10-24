# ADR 0029: Dated sale and harvesting policies share actual household funding

Status: further market/lot integration for open ticket #8. Reuses the existing sale selector, cumulative original-share targets, concentration calculations and long-only harvest pair engine. Extends [household lots](0025-household-lot-funding.md) and [shared market execution](0027-household-market-execution.md); no second trade engine or new dependency.

## Monthly observed decisions

Supported dated policies are retain, sell all permitted shares, cumulative original-share fractions, gross pre-tax household concentration targets, and conditional long-only replacement harvesting. Household policy dates must be month ends. Explicit manual trades retain their earlier monthly convention; policy sales run after them, then replacement pairs, then one sweep of remaining brokerage cash and one recognition delta into the shared household return. Existing funding sales can subsequently meet current obligations and actual tax needs.

Each policy receives the actual linked marks at that month end. The standalone schema's supplied quote fields remain in source inputs but do not override household execution marks. No later monthly return can choose an earlier policy trade. Dated and factor liquidity restrictions still apply; either a locked source or locked replacement blocks the pair without erasing wealth. Harvested losses retain the existing federal/NJ wash rules, separate bases and original-year January reconciliation.

Cumulative fractions reuse original-lot identity and include earlier ordinary funding sales. A preset fraction cannot sell original shares a second time merely because another adapter already sold them. Replacement shares receive actual purchase cost/basis and become later holdings in the same book. Cash yield on subsequent months uses those actual remaining/replacement positions.

## Household concentration includes swept cash

The shared positions calculation now includes an explicit external-wealth value, zero by default for standalone books. Household execution supplies unlinked wallet asset values, while the linked book supplies its actual shares and unswept brokerage cash. This prevents a sale's cash sweep from making its stock weight falsely return to 100% in the next decision.

The denominator is gross pre-tax household assets, consistent with the market outcome concentration diagnostic. It is not liquidation wealth or a guarantee of a concentration limit after future tax/spending. Household tax payments and spending can change the later weight, which is reported separately. The outside value cannot finance a purchase: actual available cash remains the purchase constraint.

## Explicit scope limits

Tax-budget policies still block in household execution: their standalone annual forecast cannot silently become household YTD income or use known future realized returns. They require a dated annual-forecast adapter. Manager fee schedules, issuer distributions, wrapper lots, general rebalancing/completion purchases and hypothetical terminal exits retain their separate integration guards. Market cash yield remains the explicitly confirmed monthly ordinary-character convention from ADR 0027.

Replacement eligibility and distinct wash groups are user-supplied assumptions. Synthetic examples do not establish that particular real securities avoid a wash sale or track each other perfectly. Harvest losses create no cash by themselves; only actual shared-return tax payments/refund receipts affect household cash. Matched policies reuse the same realized paths and households.

## UI and independent checks

Markets / Household funding offers Funding only, Staged sales, Concentration target and Harvesting synthetic starters. Existing household lot JSON supports the same dated policy inputs. Actual sale/harvest decisions appear beside selected-path results, in household output and in exported ledgers.

Independent checks include:

- With $1,000 cash and 1,000 shares at $100, a 50% household target sells 495 shares and retains $50,500 stock against $50,500 cash. A repeated target sells zero after the cash sweep. An irrelevant supplied $999 standalone quote cannot change the actual $100 household execution.
- With $2,000 monthly spending, initial $1,000 cash and zero commission, January ordinary funding sells ten shares. February's cumulative 2% policy sells only ten more; March's 3% target sells zero because intervening funding already reached thirty original shares.
- A one-dollar policy commission reduces ending capital by one dollar, once.
- After a 50% loss, harvesting the 600 high-basis shares produces a $24,000 federal loss and $30,000 actual replacement basis. With no ordinary income/gains to use it, terminal capital carry stays $24,000, no refund is fabricated, and matched terminal wealth remains $51,000.
- Source/replacement liquidity locks, month-end/forecast guards, immutable source cases and the actual policy UI protect execution boundaries.
