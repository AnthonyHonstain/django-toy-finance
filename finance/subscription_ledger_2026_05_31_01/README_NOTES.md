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
