Test fixtures for Vulcan's category-level fix (T-4.8). Not real fixes.

The integration tests feed these patches to Vulcan through a scripted fake model, in BR-9 order.
Each patch is relative to the state after the accepted patches before it, as a real category run
produces them:

| Patch | Applies to | Expected result |
|---|---|---|
| `good-1.patch` | original `app.py` | Fixes 101-1 (`/search`) with a parameterised query. Adds one line, so every later line in `app.py` moves down by one. |
| `good-2.patch` | `app.py` after `good-1.patch` | Fixes 101-2 (`/orders`) with a parameterised query. Its hunk starts one line lower than in the original file. |
| `partial-2.patch` | `app.py` after `good-1.patch` | Blocks only the UNION style for 101-2; boolean injection still works. Exploit gate FAILS. |
| `good-3.patch` | original `catalog.py` | Fixes 101-3 (`/products`) with a parameterised query. |
| `both-1-2.patch` | original `app.py` | Fixes 101-1 AND 101-2 in one patch (a real model reply for 101-1). Changes 101-2's lines, so the scope rule rejects it for 101-1. |
