# Workflow and Owner-Supplied Project Facts

## Authority and Scope

Source: owner-provided project goals and the 2026-11-05 onboarding instruction.
These facts describe the requested project, not verified product functionality.

- Project: line-note-order-sync, a local-first LINE Note group-buy order tool.
- Intended stack: Python 3.12, SQLite, pytest; Windows UIA is an optional adapter to be evaluated.
- Owner-selected posture: medium risk, with completeness checks and human reconciliation for buyer data and procurement quantities.
- Owner decision (2026-11-05): MVP may group buyers by nickname within one community, accepting same-name/rename risk; preserve raw comment occurrences and manual split/merge corrections. This is grouping, not proof of stable source identity or edit events.
- P0: one note, manual import, explicit SKU/quantity grammar, repeat-import safety, traceable CSV and a bounded capture feasibility experiment.
- P1: modification/cancellation support, scheduled capture and Google Sheets, each with separate evidence.
- Current state: the dependent manual POC implements JSON import, strict parsing, SQLite, audited review, accepted snapshots and CSV/HTML reports. TXT/YAML order import and real-source acceptance remain unverified.
- The owner selected this Mac for the initial capture experiment. Capture evidence records the selected window's exposed accessibility text or a manual UTF-8 copy. It stays separate from order import and carries UNKNOWN or PARTIAL completeness.
- The Mac screenshot workflow uses local Vision OCR and exports text and literal-text Excel cells after scope and count checks. The manual mode uses operator scrolling. The named-post mode validates the notebook window, searches and scrolls within it, and requests operator input for uncertain readings. Cloud transfer is separate from local execution.
- Mac navigation runs as a separate local adapter. It requests LINE's public app launch, checks the target chat before opening its notebook, and hands the selected window ID to the OCR adapter. LINE owns sign-in and operator verification remains in the capture path.
- The LINE-to-Mei handoff keeps raw occurrences and per-topic nickname totals on the Mac. An operator-reviewed export adapts product codes, confirmed prices and file-local buyer blocks to the existing Mei `包書明細` preview. Mei owns buyer identity, duplicate review and draft save; the Mac command has no network writer.
- Weekly capture separates feed inventory and eligibility from comment collection. The report window is based on publication dates in Taipei, and only posts with a confirmed elapsed cutoff enter the comment capture path. Each confirmed product code retains its own quantities, and incomplete nicknames remain pending per occurrence.

## Workflow

- Root PLAN.md owns current scope. docs/PLAN.md and docs/SLICES.md provide the design and slice acceptance cases.
- Governance source: pinned ai-governance-framework submodule from Gavin0099/ai-governance-framework.
- Local hooks must be installed on each clone; instruction files alone do not prove host execution.
- Session-derived daily, review and active-state entries use the canonical memory_record writer.
- Actual inputs and buyer data stay in ignored local paths; committed fixtures use synthetic data.
