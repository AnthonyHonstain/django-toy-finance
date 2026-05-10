# Wallet Practice 2026-05-10 01

This folder is a fresh interview-practice workspace. The goal is to practice
turning a small financial API into working code under test pressure: reading a
contract, choosing simple data structures, growing behavior phase by phase, and
managing complexity without overbuilding.

The setup is intentionally small:

* `wallet_interface.py` defines the API and reference scenarios.
* `wallet_impl.py` contains a stub implementation for you to fill in.
* `finance/tests/wallet_practice_2026_05_10_01/` mirrors this package with
  placeholder tests.

Suggested workflow:

1. Pick one behavior from the interface docstrings.
2. Turn it into a focused test.
3. Implement only enough code to pass that test.
4. Refactor when repeated logic or awkward state starts to appear.
5. Run `poetry run pytest -q`, `poetry run mypy .`, and `poetry run black .`.

Try to keep the early solution boring. A dictionary of user IDs to balances or
ledger entries is enough for the first pass. Add abstractions only when they
make the next phase easier to reason about.
