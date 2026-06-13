# Subscription Ledger Notes

2026-05-31
* Practice run created as a follow-up to the wallet ledger attempts.
* Intended pressure points:
  * append-only ledger design
  * transaction IDs and structured responses
  * scheduled recurring billing
  * idempotency
  * statement opening balances
  * revenue ranking and reversal semantics
* 0754-0756 reading through the problem
  * I read through it, I should probably think more, but I would like to get started writing some code.
* 0754-0814 start building create_customer and add_credit + balance
  * 0802 implemented create_customer, but I feel like there is more pythonic way to it using modern language features.
  * RESULT - it went okay, I stumbled on how to get a string enum of an int enum.
* 0814-0830 reviewing my work, can I loop in code coverage to help me look over my work and spot gaps?
  * I was missing the django plugin in my updated intellij, once I had the django plugin code coverage was an option (in the IDE again)
  * RESULT - That looks better, I am not gonna have code coverage tools in an interview, but it helps get my attention earlier, so I think its worth having in my practice program.

AGENT review 2026-05-31
* Clean Phase 1 start. `create_customer`, `add_credit`, `charge`, and `balance`
  are implemented with reasonable per-customer account state and ledger entries.
* Good hardening follow-up:
  * `customer_accounts` is typed, so mypy passes.
  * `Ledger` now stores transaction IDs.
  * `Ledger` now stores charge descriptions.
* Checks:
  * `poetry run mypy finance/subscription_ledger_2026_05_31_01 finance/tests/subscription_ledger_2026_05_31_01` passes.
  * Focused pytest is currently `6 passed, 5 failed`.
* The 5 failing tests are later-phase tests hitting `NotImplementedError` for
  subscription status, subscribe, billing, statement, revenue ranking, and
  reversal behavior.
* Small cleanup notes:
  * `CustomerAccount.add_ledger()` should declare `-> None`.
  * `tranx_id` works, but `transaction_id` would be clearer.
* Next good step: either re-skip later-phase tests to keep Phase 1 green, or
  start Phase 2 with `subscribe`, `cancel`, and `subscription_status`.


2026-06-13
* Pick up where I left off
* 0825-0900 start on the subscribe and run billing
  * How I am thinking about this, subscriptions live initially on the customer specific object.
  * The evidence of a billing run would be on the ledge at a minimum, but I was contemplating the tradeoffs of indexing the subscription billings independently so billing runs didn't have to look at much of the ledger.
    * This feels like where I am starting to try and think of the problem in a practical sense of how I would actually persist data, but this problem is specifically carved to avoid to much persistence.
  * So my initial plan of attack 1) attach subscriptions to customer 2) subscription runs de-dupe against existing ledger 3) optimize if needed
* 0900-0930 I am just now getting to run_billing, I spent half an hour on subscribe, cancel, subscription_status
  * I had to make a bunch of tradeoffs, using a dict of subscriptions on the customer record feels like it just made a mess.
  * I lifted the is-active logic up to the subscription record to try and re-use that code between run_billing and subscription_status
  * Tests pass, but I feel like I was never really aligned with the tests and the use cases around subscriptions+billing.

AGENT review 2026-06-13
* Phase 2 is functionally complete. Subscription creation, cancellation,
  status lookup, recurring billing, and same-timestamp idempotency are implemented.
* Good design choices:
  * Subscription activity rules live on `Subscription.is_active()`.
  * Recurring charges use the existing ledger as the billing record.
  * Billing deduplication avoids adding another index before it is needed.
* Checks:
  * Focused pytest is `8 passed, 3 failed`.
  * The 3 failures are expected Phase 3 `NotImplementedError` cases.
  * Focused mypy passes with no issues.
* Before extending the model, add tests for repeated subscribe/cancel,
  historical status lookup, cancellation boundaries, and insufficient balance.
* Next good step: implement Phase 3 statements first; this will exercise the
  ledger model before revenue ranking and reversal add more state.
