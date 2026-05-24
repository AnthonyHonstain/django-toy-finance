
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
