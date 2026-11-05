# Governance Surface Rules

Status: extracted from AGENTS.md
Semantic change: no
Runtime behavior change: no
Enforcement change: no

## Purpose

This file is a conditional router target for governance-sensitive file changes.
It provides reviewer-facing guidance for identifying authority, scope, evidence,
and claim boundaries when governance surfaces are touched.

## Governance-Sensitive Surfaces

Governance-sensitive surfaces include:
- `contract.yaml`
- `governance/RULE_REGISTRY.md`
- `governance/AGENT.md`
- `runtime_hooks/**`
- `governance_tools/**`
- `schemas/**`
- `.github/workflows/**`
- `fleet/**`
- memory writer files
- closeout files
- gate policy files

## Required Posture When These Surfaces Are Touched

When these files are touched:
- do not treat the task as a normal documentation or implementation change;
- identify the authority source;
- state allowed and forbidden scope;
- include required evidence;
- avoid enforcement, threshold, or framework-correctness claims without
  artifact-backed evidence;
- separate documentation-only changes from runtime/hook/validator behavior
  changes;
- keep claim ceiling and non-claims explicit.

## Escalation Examples

- `contract.yaml` touched: require authority / precedence analysis.
- domain contract touched: require domain authority / source trace / fail-closed posture.
- `runtime_hooks/**` touched: require runtime hook contract and safety boundary.
- `.github/workflows/**` touched: require release/CI gate and rollback evidence.
- memory writer touched: require canonical writer and memory evidence boundary.
- fleet updater touched: require fleet scope and repo allowlist boundary.
- enforcement, blocking, or complete claims: require claim ceiling and evidence maturity disclosure.
- declared scope differs from actual diff: report scope violation or require re-contract.

## Non-Claims

This file is a conditional router target.

It is not:
- a path-surface classifier
- a fail-closed enforcement implementation
- proof that Minimal Rule Selection is operational
- proof that agent context is hard-constrained to minimal rules
- a runtime hook behavior change
- a validator behavior change
