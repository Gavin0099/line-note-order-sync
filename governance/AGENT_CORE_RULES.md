---
audience: agent-on-demand
authority: canonical
can_override: false
overridden_by: SYSTEM_PROMPT.md
default_load: on-demand
---

# Agent Core Rules (canonical)

This file is the single canonical source for the agent core rules that every
agent surface must carry identically. The body between the
`ai-governance:agent-core-rules` BEGIN/END markers is projected byte-for-byte
(after newline normalization) into:

- `governance/agent-contract-template.md` — installed into a consumer's
  `AGENTS.md` (Codex), `CLAUDE.md` (Claude Code) and `GEMINI.md` (Gemini);
- `governance/copilot-instructions-template.md` — installed into
  `.github/copilot-instructions.md` (Copilot);
- this repository's own `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` and
  `.github/copilot-instructions.md`, which the framework itself loads.

`tests/test_agent_core_rules_projection.py` fails when a projection drifts.
Edit the body here first, then copy it unchanged into both templates and the
four root entry files.

Origin: owner ruling C1-C7 adopted 2026-10-30
(`docs/proposals/i2-core-rules-20261030.md`). The body is deliberately short:
it states the rules every agent needs even when no other governance document
is loaded. It does not replace `AGENTS.base.md`, `governance/SYSTEM_PROMPT.md`
or `governance/MEMORY_PROTOCOL.md`; where it names a memory target it follows
`SYSTEM_PROMPT.md` section 6.1.

<!-- ai-governance:agent-core-rules BEGIN version=1 canonical=governance/AGENT_CORE_RULES.md -->
## Agent Core Rules (MANDATORY)

Identical on every agent surface. Repository rules may add duties; they never relax these.

1. **Owner Gate.** Every agent needs explicit owner approval before merging into main, publishing or releasing, deleting branches, closing another person's PR, any irreversible operation, firmware operations, data-integrity operations, and any high-risk operation this repository's own rules name. No directive, slice approval or protocol relaxes this gate.
2. **Commit and push.** Memory and delivery protocols define order, not git authority. Commit and push follow the owner's current authorization and this repository's rules; inside an owner-authorized slice they may continue without re-asking. If either is missing from your context, ask.
3. **Task DONE is not session end.** After task DONE, stop and do no extra work. A confirmed session end still requires the existing session-end closeout. An ordinary Stop event, a final answer, or a subagent finishing is not session end.
4. **Must-record events.** Memory or PLAN updates these events require are part of that delivery, not extra work. A task limited to named files still includes these records unless the owner explicitly excludes them. After DONE, add no unrelated rollups or new PRs; do not record micro-steps or duplicate a record. Repository-specific record duties still apply. An agent's private or tool-provided memory (for example Claude auto-memory or the Copilot memory tool) may help the agent, but never satisfies these records; only the records named here or by this repository, written through their own contracts, do.

| Event | Record in |
|---|---|
| Architecture decision | `memory/02_workflow.md`; `PLAN.md` only when it changes PLAN scope, phase, anti-goal or another existing PLAN obligation |
| Bug fixed with root cause identified (new gotcha / solution) | `memory/03_knowledge_base.md` as a `CANDIDATE / UNREVIEWED` entry (root cause, fix, fix commit, test evidence) paired with a `memory_record` daily record for the same fix commit; never marked approved, reviewed only through promotion |
| Review completed | full record in `memory/04_review_log.md`, one-line summary in `memory/01_active_task.md` |
| Milestone reached | `memory/01_active_task.md`; `PLAN.md` phase/sprint only when it changes PLAN phase, scope, anti-goal or another existing PLAN obligation |
| Risk or incident encountered | `PLAN.md` risk section + `memory/01_active_task.md` |
| Confirmed session end | canonical `memory/YYYY-MM-DD.md` record through the session-end closeout when it is non-stateless |

Use an alias only when this repository has adopted the `SYSTEM_PROMPT.md` section 6.1 alias schema (`02_project_facts.md`, `03_decisions.md`, `04_validation_log.md`); never assume an alias that does not exist.

5. **No fabricated evidence.** Never claim a document was loaded, an authorization was given, or work was completed without evidence in this context. Filling `LOADED` or any other contract field by inference, or reusing a stale `[Governance Contract]` block such as one from an earlier session, is a governance failure. The block is evidence of what was loaded, not a formatting ritual.
6. **Report labels follow the session language:** Chinese `結果：` / `原因：` / `下一步：`; English `Result:` / `Reason:` / `Next step:`.
7. **Secrets.** Never commit tokens, API keys, credentials, or secrets to the repo; never write tokens or credentials into memory/ files or logs.
<!-- ai-governance:agent-core-rules END -->
