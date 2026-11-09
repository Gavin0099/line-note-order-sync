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
