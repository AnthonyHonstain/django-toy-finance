# Subscription Ledger 2026-09-13 01

This is a fresh interview-practice problem. It revisits subscription billing
without copying the May implementation: plans now live in a catalog, customers
can change plans, and reporting ranks plan revenue rather than customer spend.

The goal is to practice translating a compact contract into code, selecting
simple data structures, and handling state transitions and idempotency without
agent assistance.

## Files

- `subscription_interface.py` defines the contract and billing rules.
- `subscription_impl.py` is the empty implementation surface.
- `README_NOTES.md` is a place to record timing, decisions, and friction.
- `finance/tests/subscription_ledger_2026_09_13_01/test_subscription_impl.py`
  contains the scenario tests.

## Phases

1. **Catalog and accounts:** create plans and customers, add credit, and query
   balances.
2. **Subscription lifecycle:** subscribe, change plans, cancel, and report
   status.
3. **Billing:** charge active customers, handle insufficient credit, and make
   successful billing idempotent for a billing timestamp.
4. **Ledger features:** produce statements and rank plans by revenue.

## Start here

Every scenario begins with an explicit `@pytest.mark.skip`. Remove the marker
from the first test only, implement enough to pass it, and then enable the next
scenario.

```shell
python -m pytest -q \
  finance/tests/subscription_ledger_2026_09_13_01
```

Keep the first implementation boring. Dictionaries and small dataclasses are
enough; add indexes only when a later scenario makes the scan awkward.
