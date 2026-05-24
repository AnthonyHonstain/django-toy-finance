# Wallet Practice 2026-05-23 01

This is a fresh wallet practice run for trying a different internal model after
finishing `wallet_practice_2026_05_10_01`.

The contract keeps the same broad behavior: credits, purchases, transfers,
current balance, historical balance, statements, and top customer ranking by
gross purchase activity.

The setup is intentionally non-blocking:

* `wallet_interface.py` defines the full API and reference scenarios.
* `wallet_impl.py` has explicit method stubs that raise `NotImplementedError`.
* `finance/tests/wallet_practice_2026_05_23_01/` contains skipped scenario tests
  you can unskip one at a time.

Suggested focus for this run:

1. Pick an internal model before coding, such as per-user account ledgers plus a
   global chronological event log.
2. Implement one unskipped test at a time.
3. Keep transfer metadata explicit instead of relying on positional lookup.
4. Consider statement opening balances when the requested range starts after
   earlier account activity.
5. Run `poetry run pytest -q`, `poetry run mypy .`, and `poetry run black .`.
