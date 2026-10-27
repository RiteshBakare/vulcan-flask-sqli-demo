Test fixtures for Vulcan's own patch verifier (`vulcan verify-patch`). Not real fixes.

Each patch targets the deliberately vulnerable practice app and exercises one gate outcome:

| Patch | Expected result |
|---|---|
| `good.patch` | Parameterised query, behaviour preserved. All gates PASS, including the HTTP behaviour snapshots (all 8 `snapshot_requests` of `run-profile.json` identical); blocks every bypass variant. With both recordings it reaches verification level L3 (L2 with `--no-record`). |
| `partial.patch` | Blocks only the UNION style; boolean injection still works. Exploit gate FAILS. |
| `variant-gap.patch` | Blocks only the exact original check forms; every bypass variant (case/comment/condition/canary) still succeeds. Exploit gate FAILS, naming a variant. |
| `breaking.patch` | Blocks injection but changes search to exact match. Tests gate FAILS (the behaviour gate fails too: the search snapshots differ). |
| `edits-test.patch` | Edits a test file. Policy gate FAILS before any sandbox runs. |
| `gate-blind.patch` | Parameterises the query with `instr(username, ?) > 0`. Blocks the exploit and every variant, and all 13 tests pass, but search silently stops being case-insensitive (`q=ALI` found alice before, nothing after; no test checks it). Since T-2.5 the HTTP behaviour snapshots catch it: the behaviour gate FAILS and names `search-upper-case` (body: array of 1 before, 0 after). It used to be the seed for the Reviewer (T-5.2) while behaviour compared test results only; in a real `fix` run the Reviewer no longer sees it, because the gates fail first. |
