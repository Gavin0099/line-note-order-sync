"""Run the pinned framework's existing checks against this consumer repository.

This is orchestration only: individual framework tools retain their own rules
and exit codes. It does not validate LINE capture or order correctness.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    framework = repo / "ai-governance-framework"
    if not (framework / "governance_tools").is_dir():
        print("Initialize the framework: git submodule update --init --recursive", file=sys.stderr)
        return 1

    output = repo / "artifacts/runtime/governance-onboarding/checks"
    output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(framework)
    env["PYTHONUTF8"] = "1"
    # Smoke must not update operational runtime ledgers or claim a real session.
    env["AI_GOVERNANCE_NO_LEDGER_WRITE"] = "1"
    commands = [
        ("contract", "governance_tools.domain_contract_loader", ["--contract", "contract.yaml"]),
        ("drift", "governance_tools.governance_drift_checker", ["--repo", ".", "--framework-root", "ai-governance-framework"]),
        ("hooks", "governance_tools.hook_install_validator", ["--repo", ".", "--framework-root", "ai-governance-framework"]),
        ("readiness", "governance_tools.external_repo_readiness", ["--repo", ".", "--framework-root", "ai-governance-framework"]),
        ("memory", "governance_tools.memory_workflow", ["--check", "--repo", ".", "--run-guard", "--fail-on-blocker"]),
    ]
    for event in ("session_start", "pre_task", "post_task"):
        commands.append((
            f"codex-{event}",
            "runtime_hooks.smoke_test",
            ["--harness", "codex", "--event-type", event,
             "--project-root", ".", "--plan-path", "PLAN.md", "--contract", "contract.yaml",
             "--json-output", str(output / f"codex-{event}.json")],
        ))

    results = []
    for label, module, arguments in commands:
        command = [sys.executable, "-X", "utf8", "-m", module, *arguments]
        completed = subprocess.run(
            command, cwd=repo, env=env, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, encoding="utf-8", errors="replace", check=False,
        )
        (output / f"{label}.txt").write_text(completed.stdout, encoding="utf-8")
        print(f"{label}: {'PASS' if completed.returncode == 0 else 'FAIL'}")
        if completed.returncode:
            print(completed.stdout)
        results.append({"check": label, "module": module, "exit_code": completed.returncode})

    (output / "results.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8",
    )
    return int(any(item["exit_code"] != 0 for item in results))


if __name__ == "__main__":
    raise SystemExit(main())
