# Finance Practice Area

This Django app is being used as a small interview-practice workspace for
financial/accounting-style coding problems. The goal is not to model a
production finance system. The goal is to get repeated practice reading a small
API contract, writing tests, choosing data structures, and building behavior
incrementally under some time pressure.

## Main Bank Exercise

The original exercise lives at the top level of this app:

* `bank_interface.py`
* `bank_impl.py`
* `tests/test_bank_impl.py`

This is the committed bank/account problem. It includes deposits, transfers,
top spender ranking, withdrawals, cashback timing, and payment status checks.

## Wallet Practice Runs

Folders named like `wallet_practice_YYYY_MM_DD_NN` are standalone practice
runs. Each folder is meant to capture one attempt at solving a wallet-style
interview problem.

Each practice run should usually contain:

* `README.md` with notes for that run
* `wallet_interface.py` describing the contract and scenarios
* `wallet_impl.py` containing the attempted implementation

Tests are mirrored under `finance/tests/` using the same practice folder name.
For example:

* `wallet_practice_2026_05_10_01/`
* `tests/wallet_practice_2026_05_10_01/`

This keeps each attempt isolated so old attempts can be reviewed without
blocking new practice runs.

## Current Practice Folders

`wallet_practice_2025_10_12_01` is an earlier wallet implementation that was
moved into a dedicated folder after the fact.

`wallet_practice_2026_05_10_01` is a fresh seeded practice run. It started with
an interface, stub implementation, placeholder tests, and a README. The intent
is to convert the placeholder tests into real tests and implement the behavior
incrementally.

`wallet_practice_2026_05_23_01` is a fresh follow-up run after completing the
2026-05-10 phase 2 work. It keeps the phase 2 contract but resets the
implementation and provides skipped scenario tests for trying different
abstractions.

## Suggested Workflow

For each practice run:

1. Read the interface and scenarios.
2. Write or strengthen one test.
3. Implement the smallest useful behavior.
4. Run `poetry run pytest -q`.
5. Run `poetry run mypy .`.
6. Run `poetry run black .`.
7. Leave short notes about what went smoothly and what caused friction.

The notes matter. They make it easier to see which parts of the interview loop
need more repetition: test design, data modeling, edge cases, typing, or just
moving faster with the editor and standard library.
