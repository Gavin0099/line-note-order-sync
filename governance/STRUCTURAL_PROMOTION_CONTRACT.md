# Structural Promotion Contract

> Version: 1.0.0
> Written: 2026-04-30
> Authority: Memory Authority Contract v1.0.0 §1.2
> Status: ACTIVE

---

## Purpose

`memory/00_long_term.md` contains structural long-term memory.
Without a promotion record, these sections are **candidate memory** — useful but not
governance-authoritative.

This contract defines:
- The four classification states
- The marker format that makes promotion machine-readable
- The authority rules (AI may NOT self-promote)

---

## 1. Four Classification States

| State | Meaning | Who grants it |
|-------|---------|---------------|
| `authoritative` | Human-reviewed, source-anchored, can be cited in governance decisions | Human reviewer only |
| `candidate` | AI-proposed or written without explicit human confirmation; useful but not citeable as authority | Default for AI-written sections |
| `stale` | Content may be outdated; needs review before use | AI or human may flag |
| `rejected` | Superseded or incorrect; do not cite | Human reviewer only |

**AI invariant**: AI may propose `candidate` or `stale`. AI may NOT write `authoritative` or `rejected`.
Violation = authority self-grant (same as Phase D closeout self-sign).

---

## 2. Marker Format

Each `##`-level section in `00_long_term.md` should carry markers immediately after the heading:

```markdown
## Section Name
<!-- memory_type: structural_long_term -->
<!-- promotion_status: authoritative -->
<!-- promoted_by: Gavin / 2026-04-30 -->
<!-- source_anchor: commit:dc69408 -->
```

### Minimal required markers per state

**authoritative** (human-only to grant):
```
<!-- memory_type: structural_long_term -->
<!-- promotion_status: authoritative -->
<!-- promoted_by: <reviewer_id> / <date> -->
<!-- source_anchor: commit:<hash> | session:<id> | review:<doc> -->
```

**candidate** (AI-writable):
```
<!-- memory_type: structural_long_term -->
<!-- promotion_status: candidate -->
<!-- proposed_by: ai / <date> -->
```

**stale** (AI or human can flag):
```
<!-- memory_type: structural_long_term -->
<!-- promotion_status: stale -->
<!-- stale_reason: <one line> -->
```

**rejected**:
```
<!-- memory_type: structural_long_term -->
<!-- promotion_status: rejected -->
<!-- rejected_by: <reviewer_id> / <date> -->
<!-- rejection_reason: <one line> -->
```

---

## 3. Promotion Flow

```
AI writes section
       │
       ▼
promotion_status: candidate   ← AI-proposed
       │
  Human review
       │
  ┌────┴────────────────────────┐
  │                             │
  ▼                             ▼
authoritative              rejected/stale
(human adds promoted_by)   (human flags)
```

**Key rules**:
- `promoted_by` field is **human-only** — AI must not fill it
- Sections without any marker default to `candidate` semantics (guard treats as unregistered)
- `authoritative` is the **only** state that can be cited in governance decisions
- Promotion does NOT expire automatically; stale-flagging is advisory

---

## 4. Guard Integration

`governance_tools/memory_authority_guard.py` reads these markers when checking
`structural_memory_auto_write`. Updated behavior:

| Marker state | Guard classification |
|---|---|
| No marker | `structural_memory_auto_write` (missing_marker) |
| `candidate` | `structural_memory_auto_write` (not_yet_authoritative) — info only |
| `stale` | `structural_memory_auto_write` (stale_section) — warning |
| `rejected` | `structural_memory_auto_write` (rejected_section) — info |
| `authoritative` without `promoted_by` | `structural_memory_auto_write` (missing_promoted_by) — warning |
| `authoritative` with `promoted_by` | **CLEAR** — counts toward authority_coverage_rate |

---

## 5. Amendment

To change this contract: create v1.1.0 with name + rationale + evidence.
Silent modification = authority contract violation.
