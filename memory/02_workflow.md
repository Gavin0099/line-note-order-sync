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
- Current state: the dependent manual POC implements JSON import, strict parsing, SQLite, audited review, accepted snapshots and CSV/HTML reports. LINE capture, TXT/YAML loading, real-source acceptance and S06 remain unimplemented/unverified.

## Workflow

- Root PLAN.md owns current scope. docs/PLAN.md and docs/SLICES.md provide the design and slice acceptance cases.
- Governance source: pinned ai-governance-framework submodule from Gavin0099/ai-governance-framework.
- Local hooks must be installed on each clone; instruction files alone do not prove host execution.
- Session-derived daily, review and active-state entries use the canonical memory_record writer.
- Actual inputs and buyer data stay in ignored local paths; committed fixtures use synthetic data.
