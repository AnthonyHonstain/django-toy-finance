# Subscription Ledger 2026-05-31 01

This practice run is a fresh financial/accounting-style exercise after the
wallet ledger attempts. The goal is to exercise the same skills in a related
but different domain: reading an API contract, choosing ledger and lookup data
structures, making timestamp behavior explicit, and growing behavior with tests.

The domain is subscription billing. A customer can receive credits, be charged,
subscribe to a recurring plan, cancel, receive statements, appear in revenue
rankings, and eventually have transactions reversed.

## Why This Problem

This problem is intentionally similar to the wallet work without being the same
problem:

* It still benefits from an append-only ledger.
* It still needs transaction IDs and structured responses.
* It still has current balance and historical statement behavior.
* It adds scheduled billing and idempotency pressure.
* It forces a choice between business transactions and ledger rows.

## Files

* `subscription_interface.py` defines the full intended API.
* `subscription_impl.py` is a stub implementation for a fresh attempt.
* `README_NOTES.md` is for time-box notes, design observations, and agent
  reviews.
* `finance/tests/subscription_ledger_2026_05_31_01/` contains skipped scenario
  tests that can be unskipped one at a time.

## Phase Plan

### Phase 1: Basic Customer Billing

Implement customer creation, credits, one-time charges, and current balance.

Primary skills:

* basic state modeling
* transaction response design
* insufficient-funds or negative-balance policy
* append-only ledger versus cached balance

### Phase 2: Subscription Plans and Billing Runs

Implement subscribe, cancel, status lookup, and `run_billing(timestamp)`.

Primary skills:

* per-customer subscription state
* scheduled processing
* idempotency: running billing twice for the same period should not double bill
* handling inactive, canceled, and missing customers

### Phase 3: Statements, Revenue Ranking, and Reversal

Implement statements, top customers by revenue, transaction lookup, and reversal.

Primary skills:

* statement opening balances
* ranking with mixed sort direction
* transaction ID lookup
* reversal semantics for credits, charges, and subscription billing
* deciding whether reversed transactions count toward revenue

## Suggested Workflow

1. Read the interface and pick one skipped test.
2. Unskip only that test.
3. Implement the smallest behavior needed for that test.
4. Refactor only when the next test exposes real awkwardness.
5. Run `poetry run pytest -q`, `poetry run mypy .`, and `poetry run black .`.
