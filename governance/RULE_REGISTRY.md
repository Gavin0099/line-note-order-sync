---
audience: agent-runtime
authority: canonical
default_load: always
---

# Governance Rule Registry

This registry describes rule packs distributed by the framework. It is the
machine-readable authority used by `governance_tools/rule_classifier.py` for
context-aware activation. External contracts may add packs through their own
`contract.yaml` `rule_roots`; those packs do not need to be catalogued here.

Machine values:

- `artifact_state`: `implemented` or `planned`
- `ownership`: `framework`, `external-contract`, or `unresolved`
- `activation_mode`: `always`, `context_aware`, `explicit_only`, or `none`
- `repo_type`: `firmware`, `product`, `service`, `tooling`, or `all`
- `task_type`: `general`, `refactor`, `release`, `review`, `onboarding`, `test`, or `all`

Operational rules:

- Only `artifact_state: implemented` entries may be activated.
- `planned` entries must use `activation_mode: none` and remain absent from
  active, preview, warning, skill, and agent outputs.
- `explicit_only` entries are never selected by context classification. They
  load only when explicitly requested by runtime rules or a contract.
- Unknown metadata fields are forward-compatible and must not break parsing.
- `load_mode` is a legacy parser alias for `activation_mode`; new registry
  entries use `activation_mode` only.

## Quick Reference

| Pack | Artifact | Ownership | Activation | Purpose |
| --- | --- | --- | --- | --- |
| `common` | implemented | framework | always | Core coding baseline |
| `cpp` | implemented | framework | context-aware | C and C++ rules |
| `csharp` | implemented | framework | context-aware | C# rules |
| `python` | implemented | framework | context-aware | Python rules |
| `gdscript` | implemented | framework | explicit-only | GDScript context; native checks belong to the consumer contract |
| `swift` | implemented | framework | context-aware | Swift rules |
| `avalonia` | implemented | framework | context-aware | Avalonia UI rules |
| `refactor` | implemented | framework | context-aware | Refactoring rules |
| `kernel-driver` | implemented | framework | context-aware | Framework driver baseline; external contracts may override it |
| `gl-hub-vendor-cmd` | implemented | external-contract | explicit-only | Contract-authorized GL hub vendor-command rules |
| `release` | planned | framework | none | Reserved release checklist slot |
| `typescript` | planned | framework | none | Reserved TypeScript/Node.js slot |
| `electron` | planned | framework | none | Reserved Electron IPC/security slot |
| `firmware_isr` | planned | unresolved | none | Reserved generic ISR slot pending authority review |

`nextjs`, `supabase`, and `review_gate` were removed as stale declarations on
2026-07-13. The decision record is
`docs/governance/2026-07-13-rule-registry-classification-decision.md`.

## Rule Packs: Machine-Readable Metadata

### common

```yaml
name: common
artifact_state: implemented
ownership: framework
activation_mode: always
repo_type: [all]
task_type: [all]
risk_level: [all]
description: "Core coding standards; loaded in every session"
```

### refactor

```yaml
name: refactor
artifact_state: implemented
ownership: framework
activation_mode: context_aware
repo_type: [all]
task_type: [refactor]
risk_level: [all]
description: "Refactoring patterns; activated when task_type=refactor"
```

### release

```yaml
name: release
artifact_state: planned
ownership: framework
activation_mode: none
repo_type: [all]
task_type: [release]
risk_level: [all]
description: "Reserved release checklist slot; no framework artifact exists"
```

### typescript

```yaml
name: typescript
artifact_state: planned
ownership: framework
activation_mode: none
repo_type: [product]
task_type: [all]
risk_level: [all]
description: "Reserved TypeScript/Node.js slot; no framework artifact exists"
```

### python

```yaml
name: python
artifact_state: implemented
ownership: framework
activation_mode: context_aware
repo_type: [service, tooling]
task_type: [all]
risk_level: [all]
description: "Python coding standards for service and tooling repos"
```

### gdscript

```yaml
name: gdscript
artifact_state: implemented
ownership: framework
activation_mode: explicit_only
repo_type: [all]
task_type: [all]
risk_level: [all]
description: "GDScript context selected explicitly; consumer contracts own native validation"
```

### electron

```yaml
name: electron
artifact_state: planned
ownership: framework
activation_mode: none
repo_type: [product]
task_type: [all]
risk_level: [all]
description: "Reserved Electron IPC/security slot; no framework artifact exists"
```

### avalonia

```yaml
name: avalonia
artifact_state: implemented
ownership: framework
activation_mode: context_aware
repo_type: [product]
task_type: [all]
risk_level: [all]
description: "Avalonia UI component and threading rules"
```

### cpp

```yaml
name: cpp
artifact_state: implemented
ownership: framework
activation_mode: context_aware
repo_type: [firmware, product]
task_type: [all]
risk_level: [all]
description: "C++ memory safety and RAII rules"
```

### csharp

```yaml
name: csharp
artifact_state: implemented
ownership: framework
activation_mode: context_aware
repo_type: [product]
task_type: [all]
risk_level: [all]
description: "C# async patterns and null safety rules"
```

### swift

```yaml
name: swift
artifact_state: implemented
ownership: framework
activation_mode: context_aware
repo_type: [product]
task_type: [all]
risk_level: [all]
description: "Swift value-type safety and concurrency rules"
```

### firmware_isr

```yaml
name: firmware_isr
artifact_state: planned
ownership: unresolved
activation_mode: none
repo_type: [firmware]
task_type: [all]
risk_level: [all]
review_by: 2026-10-13
description: "Reserved generic ISR slot pending firmware versus kernel authority review"
```

### kernel-driver

```yaml
name: kernel-driver
artifact_state: implemented
ownership: framework
activation_mode: context_aware
repo_type: [firmware]
task_type: [all]
risk_level: [all]
authority_note: "Framework baseline; a contract-local pack with the same name overrides it"
description: "Generic kernel/driver baseline for KDC and similar driver repos"
```

### gl-hub-vendor-cmd

```yaml
name: gl-hub-vendor-cmd
artifact_state: implemented
ownership: external-contract
activation_mode: explicit_only
contract_domain: gl-hub-vendor-cmd
repo_type: [product]
task_type: [all]
risk_level: [all]
distribution_note: "Framework copy is a compatibility mirror; external contract controls activation"
description: "GL hub vendor-command specification truth"
```

## Selection Boundary

Context-aware classification is advisory and must intersect the registry
metadata above. Runtime content loading remains fail-closed and resolves actual
pack folders. External contract rule roots precede the framework rule root, so
a contract-local pack may intentionally override a framework baseline.

Explicit runtime rules have final authority. Heuristic suggestions never load a
pack automatically.
