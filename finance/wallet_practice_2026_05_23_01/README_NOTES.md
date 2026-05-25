
2026-05-24
* 0735-0746 starting on the core datastructures.
* RESULT - Got a dataclass for ledger in place, an enum, and a wallet class that I can 
  use to organize each of individual peoples records.
* 0746-0800 implemented credit and balance, they went very smooth.
* 0800-0815 going for purchase and transfer
  * RESULT - This went pretty well, I was reasonably pleased with how legible the code was.
  * RESULT -  I still feel like my check on is the user exists could be cleaner.
    * On the plus side, in its current form its pretty readable and explicit.
* 0817-0835 starting on the statement implementation.
  * PLANNING - Oh right - they folded in a rolling balance on the statement. I hadn't 
    really wanted to pre-compute a balance on the ledger, it was my instinct to not persist 
    that kind of aggregation on each ledger (then you potentially have to re-touch all of 
    them if you need to make a change in the future - your mixing concerns into the double 
    entry accounting append ledger)
  * RESULT - It went all right, the custom formatting logic ended up being all in once 
    place and I was able to cleanly compute it using what I had in the per-user ledger.
* 0836-0846 going to rush and see if I can get through the top_customers
  * RESULT - Got hung up on map built in, but otherwise it was okay. I don't seem to get 
    to use map very often. 

References:
* https://docs.python.org/3/whatsnew/3.8.html
* https://docs.python.org/3/tutorial/controlflow.html
* https://docs.python.org/3/library/functions.html#map

AGENT review
* Checks passed for the current implementation:
  * `poetry run pytest finance/tests/wallet_practice_2026_05_23_01/test_wallet_impl.py -q`
  * `poetry run mypy finance/wallet_practice_2026_05_23_01 finance/tests/wallet_practice_2026_05_23_01`
  * `poetry run black --check finance/wallet_practice_2026_05_23_01 finance/tests/wallet_practice_2026_05_23_01`
  * `poetry run pytest -q`
* The per-user `Wallet` ledger abstraction is a real improvement over the prior
  attempt. `statement()` is easier to reason about, and explicit `transfer_to`
  / `transfer_from` fields remove the fragile positional transfer lookup.
* Main correctness gap: `transfer()` currently creates the transfer entries
  without checking that the source wallet has enough balance. Add a focused test
  that an insufficient transfer returns `None` and does not mutate either wallet.
* Second correctness gap: `balance_at()` returns `0` when the user exists now
  but did not exist yet at `at_timestamp`. The interface says that should be
  `None`. Add a regression test like crediting at timestamp 5, then checking
  `balance_at(..., at_timestamp=1) is None`.
* The opening-balance statement scenario is a strong test. This implementation
  handles it cleanly by computing running balance across prior entries before
  emitting rows inside the requested range.
* Once the failed transfer and pre-existence historical balance cases are fixed,
  this version is in solid shape for the current contract.

2026-05-25
* 0902-0915 Fixing bugs from yesterday
  * transfer was allowed with insufficient funds.
  * balance at returning None 
* 0921-1004 Working on phase 3
  * I had fun thinking through the different options I had for implementing
  * Added a dictionary for uuid lookup of ledgers
  * Decided on a light optional FK to relate ledgers to one another for reversal.

AGENT review 2026-05-25
* Checks:
  * `poetry run pytest finance/tests/wallet_practice_2026_05_23_01/test_wallet_impl.py -q` passes with 18 tests.
  * `poetry run black --check finance/wallet_practice_2026_05_23_01 finance/tests/wallet_practice_2026_05_23_01` passes.
  * `poetry run mypy finance/wallet_practice_2026_05_23_01 finance/tests/wallet_practice_2026_05_23_01` fails because
    `WalletImpl.credit`, `purchase`, and `transfer` now return `WalletTxnResponse`, while `WalletInterface` still declares
    the old `int` / `int | None` return types.
* The two Phase 2 bugs from yesterday were addressed well. Transfer now checks source balance before mutating, and
  historical balance now distinguishes "user exists now" from "user existed at that timestamp."
* The `WalletTxnResponse` direction makes sense for Phase 3 because callers need transaction IDs to test reversal.
  The next cleanup is to make that contract explicit in `wallet_interface.py` and its docstrings, or choose a separate
  method for transaction-bearing operations if you want to preserve the earlier API shape.
* The ledger lookup dictionary is the right kind of pressure-driven abstraction. It avoids scanning the whole global
  ledger for reversal and makes unknown transaction handling straightforward.
* The append-only reversal model is a good accounting instinct. Mutating the original ledger only to record
  `reverse_txn_id` is reasonable metadata, while the financial effect is represented by a new reverse ledger.
* Current Phase 3 coverage handles unknown reversal, credit reversal, purchase reversal, insufficient credit reversal,
  and idempotency. Still open: `transaction()` is unimplemented, transfer reversal is unimplemented, and the intended
  effect of reversing a purchase on `top_customers()` needs an explicit contract decision.
* Test precision note: `test_reverse_purchase_single` uses `ANY` for the original credit row's `reverse_txn_id`, which
  would also accept an accidental mutation of the credit ledger. If the purchase reversal should only mark the purchase,
  assert `reverse_txn_id=None` on the credit row.
* Overall: this was a useful Phase 3 start. The core data model is bending in the right direction, but the public
  interface should be reconciled before adding more reversal behavior so tests, types, and API docs all describe the
  same contract.
