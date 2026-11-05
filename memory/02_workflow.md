# Workflow and Owner-Supplied Project Facts

## Authority and Scope

Source: owner-provided project goals and the 2026-11-05 onboarding instruction.
These facts describe the requested project, not verified product functionality.

- Project: line-note-order-sync, a local-first LINE Note group-buy order tool.
- Intended stack: Python 3.12, SQLite, pytest; Windows UIA is an optional adapter to be evaluated.
- Owner-selected posture: medium risk, with completeness checks and human reconciliation for buyer data and procurement quantities.
- P0: one note, manual import, explicit SKU/quantity grammar, repeat-import safety, traceable CSV and a bounded capture feasibility experiment.
- P1: modification/cancellation support, scheduled capture and Google Sheets, each with separate evidence.
- Current state: product code, parser tests, capture and native LINE acceptance have not been implemented or verified.

## Workflow

- Root PLAN.md owns current scope. docs/PLAN.md and docs/SLICES.md provide the design and slice acceptance cases.
- Governance source: pinned ai-governance-framework submodule from Gavin0099/ai-governance-framework.
- Local hooks must be installed on each clone; instruction files alone do not prove host execution.
- Session-derived daily, review and active-state entries use the canonical memory_record writer.
- Actual inputs and buyer data stay in ignored local paths; committed fixtures use synthetic data.
