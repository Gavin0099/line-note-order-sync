# Knowledge Base

## Gotchas

- Record troubleshooting notes, anti-patterns, and fixes here.

## CANDIDATE / UNREVIEWED: Clean-runner prerequisites for governance onboarding

- Root cause: the initial Windows CI checkout hit Git's long-path limit in the pinned framework tree; the initial Linux CI reached runtime_phase_policy.py without its imported PyYAML dependency installed.
- Fix: enable Git longpaths only on the disposable Windows runner before checkout, install PyYAML 6.0.3 from requirements-governance.txt, and document the same prerequisites for new clones.
- Fix commit: 5c267dad811da092de83fea2b498cfe72ddba569
- Test evidence: first failing run https://github.com/Gavin0099/line-note-order-sync/actions/runs/42010204828; a clean local venv with only requirements-governance.txt installed passed all eight checks. Remote rerun remains a separate delivery check.
- Daily record: memory/2026-11-05.md (memory_record, commit 5c267dad811da092de83fea2b498cfe72ddba569).
