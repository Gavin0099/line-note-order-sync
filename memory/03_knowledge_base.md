# Knowledge Base

## Gotchas

- Record troubleshooting notes, anti-patterns, and fixes here.

## CANDIDATE / UNREVIEWED: Clean-runner prerequisites for governance onboarding

- Root cause: the initial Windows CI checkout hit Git's long-path limit in the pinned framework tree; the initial Linux CI reached runtime_phase_policy.py without its imported PyYAML dependency installed.
- Fix: enable Git longpaths only on the disposable Windows runner before checkout, install PyYAML 6.0.3 from requirements-governance.txt, and document the same prerequisites for new clones.
- Fix commit: 5c267dad811da092de83fea2b498cfe72ddba569
- Test evidence: first failing run https://github.com/Gavin0099/line-note-order-sync/actions/runs/42010204828; a clean local venv with only requirements-governance.txt installed passed all eight checks. Remote rerun remains a separate delivery check.
- Daily record: memory/2026-11-05.md (memory_record, commit 5c267dad811da092de83fea2b498cfe72ddba569).

## CANDIDATE / UNREVIEWED: Audit selecting a historical accepted snapshot

- Root cause: the initial POC reused an existing accepted version and overwrote only the current pointer; selecting A after B lost the new selector's identity and time.
- Fix: v2 separates immutable acceptance versions from append-only selection events; pointer changes and selection metadata commit atomically. Reports retain original acceptance metadata and current selection actor/time; report bundle identity includes selection ID. Existing v1 POC DBs are refused unchanged rather than migrated automatically.
- Fix commit: 2677ed9853b228ee13a4714b50c64a64cb1b67c1
- Test evidence: tests/test_reconcile.py::test_historical_reselection_preserves_each_operator_without_duplicating_versions verifies Alice -> Bob -> Carol, two versions / three events, no repeat-current duplication and report metadata; v1 preservation regression and full 100-test local product suite passed. Source finding: PR #4 discussion_r4479900516.
- Daily record: memory/2026-11-05.md (memory_record, commit 2677ed9853b228ee13a4714b50c64a64cb1b67c1).

## CANDIDATE / UNREVIEWED: Keep item and buyer uncertainty through weekly export

- Root cause: a post-level nickname total can discard individual item codes before export, and a displayed nickname ending in an ellipsis cannot establish that repeated rows are from the same buyer.
- Fix: retain per-code quantities, create tabs from observed item codes, and keep clipped nickname occurrences separate with blank quantities until reviewed.
- Fix commit: 44ca5e19488b4c12055631102848a2f6382a6183
- Test evidence: tests/test_note_week.py::test_workbook_splits_items_and_never_combines_unconfirmed_nicknames checks exact cell readback for coded quantities and two unresolved occurrences in a third variant tab; 189 product tests passed, 1 platform case skipped.
- Daily record: memory/2026-11-09.md (memory_record, commit 44ca5e19488b4c12055631102848a2f6382a6183).

## CANDIDATE / UNREVIEWED: Retry a stationary LINE feed before ending relocation

- Root cause: post relocation treated one zero-motion scroll as the feed boundary; the live UI temporarily stopped moving before reaching the target.
- Fix: share the inventory's delayed retry between inventory and relocation; preserve timestamp, position and image checks before opening comments.
- Fix commit: 5bdb20cd6e1f25adc8a474e3b1b35445eb970f37
- Test evidence: tests/test_note_week.py::test_locate_post_retries_idle_scroll_without_accepting_another_card, 190 product tests passed with one platform skip, and live weekly export readback verified the only eligible closed post.
- Daily record: memory/2026-11-09.md (memory_record, commit 5bdb20cd6e1f25adc8a474e3b1b35445eb970f37).

## CANDIDATE / UNREVIEWED: Taipei cutoff parsing without platform timezone data

- Root cause: Windows runners had neither a system IANA timezone database nor the optional Python timezone package. Importing the weekly parser raised before test collection.
- Fix: use the platform Taipei timezone when present; fall back to UTC+08:00 for current LINE cutoff dates when the database is unavailable.
- Fix commit: 3cbabc4b026e30dbf7d4ee35b7655565ee8dfa33
- Test evidence: GitHub Actions run 42609754159 reproduced `ZoneInfoNotFoundError`; 190 product tests passed with timezone data disabled locally, and the Taipei midnight cutoff independently converted to the expected UTC instant.
- Daily record: memory/2026-11-09.md (memory_record, commit 3cbabc4b026e30dbf7d4ee35b7655565ee8dfa33).

## CANDIDATE / UNREVIEWED: Do not use a partial clock as a cutoff

- Root cause: optional clock parsing used a numeric prefix of the cutoff and silently discarded a following PM marker or malformed suffix. A Chinese evening twelve could also be treated as noon.
- Fix: validate the complete clock in the cutoff clause, handle explicit AM/PM, and require review of ambiguous or malformed times.
- Fix commit: 053d6989b98aa7a9eeda7f06be561e60bfb31788
- Test evidence: the original code opened synthetic posts before PM or ambiguous cutoffs; the weekly regression verifies that neither is opened and that 23:30 appears in the correct report row. Full suite: 207 passed, 1 platform skip.
- Daily record: memory/2026-11-10.md (memory_record, commit 053d6989b98aa7a9eeda7f06be561e60bfb31788).

## CANDIDATE / UNREVIEWED: Check the comment icon before applying a feed date boundary

- Root cause: inventory trusted date-shaped OCR lines as post footers before visual verification, so body dates could trigger the older-post stopping condition.
- Fix: require the existing comment icon check before partitioning cards or counting older ones; if two known-author headers fall before one verified footer, refuse to treat the scan as complete.
- Fix commit: 053d6989b98aa7a9eeda7f06be561e60bfb31788
- Test evidence: synthetic body dates no longer hide the real in-range card, and a missing intermediate footer refuses the report. Native OCR replay of previously captured screenshots matched the original inventory totals.
- Daily record: memory/2026-11-10.md (memory_record, commit 053d6989b98aa7a9eeda7f06be561e60bfb31788).

## CANDIDATE / UNREVIEWED: Keep adjacent authors separated after a missed footer

- Root cause: discarding an unverified footer could join its post to a later ordinary author's card. The known-author name check alone could not see that boundary.
- Fix: if a date-shaped OCR row without a verified footer is followed by a possible new header at the observed layout positions, refuse the report before opening any comments. A footer verified in an overlapping frame is still usable.
- Fix commit: 053d6989b98aa7a9eeda7f06be561e60bfb31788
- Test evidence: reproduced before the fix for a synthetic ordinary author; the final regression covers ordinary and admin headers, overlapping verification, and preserved captured inventory counts. 207 product tests passed, 1 platform skip.
- Daily record: memory/2026-11-10.md (memory_record, commit 053d6989b98aa7a9eeda7f06be561e60bfb31788).
