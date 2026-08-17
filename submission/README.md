# Evidence — Lab 17

Nguyen Le Minh — 2A202601045

Captured terminal output for the four required evidence items:

| File | Covers | Result |
| --- | --- | --- |
| `long_term.log` | E02, E03, E08, E09 | 4/4 PASS |
| `episodic.log` | E04, E05 | 2/2 PASS |
| `semantic.log` | E06, E11 | 2/2 PASS |
| `privacy_forget.log` | forget + `--verify-only` | `Zep user absent: True`, `Redis user keys remaining: 0` |

Order of operations for the privacy drill: the full student benchmark was run
and committed **first**, then `src.forget --user-id minh-lab17`, then
`--verify-only`, then `src.seed` to restore the graph, then the full benchmark
was re-run to confirm 11/11 still holds on the re-seeded graph.

> Note: these are terminal **logs**, not `.png` screenshots. The mark scheme
> accepts "screenshot/log" for the privacy drill; for `long_term.png`,
> `episodic.png` and `semantic.png` take real screenshots of the commands in
> `long_term.log` / `episodic.log` / `semantic.log` re-run in your terminal.
