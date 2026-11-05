# Governance Authority Table

<!-- mrcsp_activation_id: mrcsp-m1-authority-reader-v1 -->

> machine-readable: true
> version: 1.1.0
> updated: 2026-10-30


> Authority-loader note: `runtime_hooks/core/session_start.py` derives the live
> authority filter from each `governance/*.md` file's frontmatter through
> `governance_tools.authority_loader`. This table is the human-facing registry
> and must mirror that frontmatter; table-only edits do not change live
> `allowed_governance_files` behavior.

## Authority Levels

- `canonical`：最高權威來源。若與其他來源衝突，以它為準；其他只能是 derived 或補充層。
- `reference`：輔助性權威來源。可提供解釋與判準，但不能覆蓋 canonical。
- `derived`：由 canonical / reference 推導出的工作性輸出，可快取、摘要、投影，但不能反向覆蓋上游真相。

These labels classify governance-document precedence. They do not collapse
canonical storage, canonical writer format, and authority for a particular
question into one property. Memory surfaces use the question-specific roles in
`MEMORY_SURFACE_AUTHORITY_CONTRACT.md`.

## Audience Types

- `agent-runtime`：在 `session_start` 或等效 runtime path 中會被直接讀入
- `agent-on-demand`：只在特定情境、特定 task 類型下按需讀入
- `human-only`：提供給人類 reviewer / operator 參考，不屬於 agent 預設 runtime 載入面

## Default Load Modes

- `always`：每次 session 都應載入；通常只給 canonical / derived 的 agent-runtime surface
- `on-demand`：只有當 context 需要時才讀
- `incremental`：只增量讀取最近候選，不做 full rescan
- `never`：agent 不自動載入；通常對應 human-only 文件

---

## Authority Table

| document | audience | authority | can_override | overridden_by | default_load |
|----------|----------|-----------|--------------|---------------|--------------|
| `governance/SYSTEM_PROMPT.md` | agent-runtime | canonical | false | ~ | always |
| `governance/AGENT.md` | agent-runtime | canonical | false | ~ | always |
| `governance/RULE_REGISTRY.md` | agent-runtime | canonical | false | ~ | always |
| `governance/AGENT_CORE_RULES.md` | agent-on-demand | canonical | false | SYSTEM_PROMPT.md | on-demand |
| `governance/RUNTIME_CONTRACT.md` | agent-runtime | canonical | false | ~ | on-demand |
| `governance/PLAN.md` | agent-on-demand | reference | false | ../PLAN.md | on-demand |
| `governance/MEMORY_PROTOCOL.md` | agent-runtime | canonical | false | AGENT.md | on-demand |
| `governance/MEMORY_SURFACE_AUTHORITY_CONTRACT.md` | agent-on-demand | canonical | false | AGENT.md | on-demand |
| `governance/MEMORY_RECONCILIATION_FIXTURE_ADMISSIBILITY_CONTRACT.md` | agent-on-demand | canonical | false | AGENT.md | on-demand |
| `governance/MEMORY_RECONCILIATION_EXACT_BYTE_DETECTOR_CONTRACT.md` | agent-on-demand | canonical | false | AGENT.md | on-demand |
| `governance/MEMORY_RECONCILIATION_ENCODING_INTEGRITY_CONTRACT.md` | agent-on-demand | canonical | false | AGENT.md | on-demand |
| `governance/MEMORY_RECONCILIATION_KNOWLEDGE_IDENTITY_CONTRACT.md` | agent-on-demand | canonical | false | AGENT.md | on-demand |
| `governance/MEMORY_RECONCILIATION_MISSING_LOGICAL_SURFACE_CONTRACT.md` | agent-on-demand | canonical | false | AGENT.md | on-demand |
| `governance/SOLO_OWNER_MERGE_AUTHORITY_CONTRACT.md` | agent-on-demand | canonical | false | AGENT.md | on-demand |
| `governance/AI_GOVERNANCE_UPDATE_PROTOCOL.md` | agent-on-demand | reference | false | AGENT.md | on-demand |
| `governance/F7_FULL_UPDATE.md` | agent-on-demand | reference | false | AGENT.md | on-demand |
| `governance/ARCHITECTURE.md` | agent-on-demand | reference | false | SYSTEM_PROMPT.md | on-demand |
| `governance/TESTING.md` | agent-on-demand | reference | false | AGENT.md | on-demand |
| `governance/NATIVE-INTEROP.md` | agent-on-demand | reference | false | AGENT.md | on-demand |
| `governance/RESPONSE_ENVELOPE_CONTRACT.md` | agent-runtime | reference | false | AGENT.md | on-demand |
| `governance/HUMAN-OVERSIGHT.md` | human-only | reference | false | ~ | never |
| `governance/REVIEW_CRITERIA.md` | agent-on-demand | reference | false | AGENT.md | on-demand |
| `governance/PHASE_D_CLOSE_AUTHORITY.md` | human-only | canonical | false | ~ | never |
| `AGENTS.md` (workspace) | agent-runtime | derived | false | AGENT.md | always |
| `.github/copilot-instructions.md` | agent-runtime | derived | false | AGENT.md | always |
| `.github/agents/*.agent.md` | agent-on-demand | derived | false | AGENT.md | on-demand |
| `domain contract (full)` | agent-on-demand | canonical | false | ~ | on-demand |
| `domain adapter summary` | agent-runtime | derived | false | domain contract | always |
| `docs/e1-mutation-catalog.md` | agent-on-demand | reference | false | PLAN.md | on-demand |
| `governance_tools.memory_workflow` | agent-runtime | derived | false | MEMORY_PROTOCOL.md | on-demand |
| `memory/YYYY-MM-DD.md` | agent-runtime | reference | false | MEMORY_PROTOCOL.md | incremental |
| `memory/00_long_term.md` | agent-runtime | reference | false | MEMORY_PROTOCOL.md | on-demand |
| `memory/01_active_task.md` | agent-runtime | derived | false | MEMORY_PROTOCOL.md | incremental |
| `memory/02_workflow.md` | agent-runtime | derived | false | MEMORY_PROTOCOL.md | incremental |
| `memory/03_knowledge_base.md` | agent-runtime | reference | false | MEMORY_PROTOCOL.md | incremental |
| `memory/04_review_log.md` | agent-runtime | reference | false | MEMORY_PROTOCOL.md | incremental |
| `memory/reviewer_handoff_*` | agent-on-demand | derived | false | 03_knowledge_base.md | on-demand |
| `memory/framework_artifact_*` | agent-on-demand | derived | false | ~ | on-demand |
| `external repo aliases` | agent-on-demand | reference | false | ~ | on-demand |

---

## Conflict Resolution Rules

衝突處理的基本順序是：

```text
canonical > reference > derived
```

具體規則：

1. `canonical` vs `reference`：以 canonical 為準，reference 只能補充或說明
2. `canonical` vs `derived`：以 canonical 為準，derived 必須被視為可失效投影
3. `reference` vs `derived`：以 reference 為準
4. workspace instruction（如 `AGENTS.md`、`copilot-instructions`）不得覆蓋 repo canonical
5. `agent-on-demand` 載入時，可以引入 reference，但不得改寫 canonical 的主張
6. `derived` 載入時，只能幫助 session_start 或 task context 收斂，不能創造新的 authority
7. Phase D completion claims: `PHASE_D_CLOSE_AUTHORITY.md` takes precedence over README,
   PLAN.md, implementation presence, version tags, commit history, and all generated
   summaries. No agent-produced signal may override this contract.
8. The global document ordering above does not resolve conflicts between memory
   surfaces that answer different question classes. Use
   `MEMORY_SURFACE_AUTHORITY_CONTRACT.md`; unresolved qualified-source conflicts
   require reviewer resolution.

---

## Memory Source Authority

| memory source | authority role | promotion policy |
|---------------|----------------|------------------|
| `memory/YYYY-MM-DD.md` | event / provenance history | not directly promotable as current state |
| `memory/00_long_term.md` | section-qualified durable context | requires valid promotion authority |
| `01_active_task.md` | reviewed current-state projection | traceable source anchors and review required |
| `02_workflow.md` and declared aliases | current operational / architecture projection | traceable source anchors and review required |
| `03_knowledge_base.md` and declared aliases | section-qualified reusable knowledge | only promoted, reviewed, non-superseded sections qualify |
| `04_review_log.md` and declared aliases | append-only review history | current verdict requires valid authority-qualified non-superseded review |
| reviewer handoff summary | derived | cache only，不得 promote 成 truth |
| framework artifact cache | derived | cache only，不得 promote 成 truth |
| external repo aliases | reference | 可視情況 promote，但仍需對照 canonical |

---


## Registered Governance Surface Notes

| surface | authority role | scope | limitation |
|---------|----------------|-------|------------|
| `governance/MEMORY_PROTOCOL.md` | canonical memory write protocol | governed memory write path, canonical writer usage, memory workflow dispatch, and memory completion claim boundaries | does not itself guarantee structured memory freshness |
| `governance/MEMORY_SURFACE_AUTHORITY_CONTRACT.md` | question-specific memory reader contract | memory surface roles, ambiguity handling, and current-state projection claim ceiling | active only through approved merge of the complete M-1 document set; no runtime reader or semantic verification |
| `governance/MEMORY_RECONCILIATION_FIXTURE_ADMISSIBILITY_CONTRACT.md` | canonical MRCSP fixture admission contract | one synthetic redacted exact-byte-duplicate test fixture, its provenance, redaction boundary, digest, and required rejection cases | no reader, detector, runtime, public schema, CI, gate, or enforcement behavior |
| `governance/MEMORY_RECONCILIATION_EXACT_BYTE_DETECTOR_CONTRACT.md` | canonical MRCSP M1a detector contract | deterministic raw-byte SHA-256 duplicate reporting for two caller-admitted records | report-only; no admission, semantic reconciliation, reader, projection, schema, runtime, hook, CI, gate, blocker, or enforcement behavior |
| `governance/MEMORY_RECONCILIATION_ENCODING_INTEGRITY_CONTRACT.md` | canonical MRCSP M1b-1 detector contract | deterministic strict UTF-8 and literal U+FFFD anomaly reporting for one caller-admitted record | report-only; no mojibake heuristic, repair, identity collision, missing surface, reader, schema, runtime, hook, CI, gate, blocker, or enforcement behavior |
| `governance/MEMORY_RECONCILIATION_KNOWLEDGE_IDENTITY_CONTRACT.md` | canonical MRCSP M1b-2 detector contract | deterministic exact case-sensitive knowledge-identity collision reporting for two caller-admitted observations | report-only; no parsing, normalization, semantic identity, missing surface, reader, schema, runtime, hook, CI, gate, blocker, or enforcement behavior |
| `governance/MEMORY_RECONCILIATION_MISSING_LOGICAL_SURFACE_CONTRACT.md` | canonical MRCSP M1b-3 detector contract | deterministic alias-aware missing-surface reporting for one caller-admitted logical memory surface | report-only; no scanning, parsing, repair, freshness, supersession, reader, schema, runtime, hook, CI, gate, blocker, enforcement, or M2 behavior |
| `governance/SOLO_OWNER_MERGE_AUTHORITY_CONTRACT.md` | canonical solo-owner merge decision contract | exact-head owner attestation, independent technical review, green required checks, and reviewed-head preservation | reporting and authority semantics only; no GitHub settings, CI, runtime, hook, gate, blocker, or enforcement behavior |
| `governance/AGENT_CORE_RULES.md` | canonical source of the agent core rules | the body between the agent-core-rules markers, projected byte-identical into `governance/agent-contract-template.md` and `governance/copilot-instructions-template.md` | `on-demand`, not `always`: the installed projections (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`) already deliver the body every session, so an `always` load would put the same rules in context twice; read this file when editing or verifying the rules |
| `docs/e1-mutation-catalog.md` | mutation contract catalog / mutation surface inventory | documents mutation-capable surfaces and their allowed claim level | catalog presence is not enforcement by itself |
| `governance_tools.memory_workflow` | implementation surface for governed memory workflow | dispatch, write-path assessment, guard summary, and receipt status reporting | implementation behavior must not exceed documented contract |

---
## Loading Condition Summary

| task_level | always | on-demand | incremental | never |
|------------|--------|-----------|-------------|-------|
| L0 | canonical runtime core | minimal reference only when needed | candidates only | human-only docs |
| L1 | canonical runtime core | boundary / testing / domain reference | candidates only | human-only docs |
| L2 | canonical runtime core | broader reference + contract context | candidates only | human-only docs |
| any | human-only surface 不自動載入 | | | |
