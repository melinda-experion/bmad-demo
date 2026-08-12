#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""UserPromptSubmit hook: screen every user prompt through PromptGateway.

Reuses the prompt-gateway-guard skill's validate_prompt.py for the actual HTTP
call rather than duplicating that logic here. Reads config (base_url, api_key,
downstream_model) via the same resolve_customization.py path the skill itself
uses, so team/user overrides in _bmad/custom/ apply here too.

Fails open: if PromptGateway can't be reached or errors, the prompt proceeds
with a warning rather than being blocked -- a screening outage should not take
down the whole project.

Decision handling:
  BLOCK -> decision:"block" (Claude never sees the prompt), reason shown to user.
  FLAG  -> prompt proceeds; a warning is shown to the user and injected into
           Claude's context as additionalContext, since a hook can't pause for
           an interactive yes/no the way the manual prompt-gateway-guard skill can.
  ALLOW -> proceeds silently.

Prints one JSON object to stdout per the UserPromptSubmit hook output contract
(systemMessage / decision / reason / hookSpecificOutput.additionalContext).
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = PROJECT_ROOT / ".claude" / "skills" / "prompt-gateway-guard"
VALIDATE_SCRIPT = SKILL_ROOT / "scripts" / "validate_prompt.py"
RESOLVE_SCRIPT = PROJECT_ROOT / "_bmad" / "scripts" / "resolve_customization.py"

DEFAULT_CONFIG = {"base_url": "http://localhost:8000", "api_key": "", "downstream_model": ""}


def resolve_agent_config() -> dict:
    try:
        proc = subprocess.run(
            ["uv", "run", str(RESOLVE_SCRIPT), "--skill", str(SKILL_ROOT), "--key", "agent"],
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
        )
        return json.loads(proc.stdout)["agent"]
    except Exception:
        pass

    # Fallback: read the skill's own customize.toml scalars directly (base config
    # only, no team/user override merge) if the resolver couldn't run.
    config = dict(DEFAULT_CONFIG)
    customize_path = SKILL_ROOT / "customize.toml"
    if customize_path.exists():
        for line in customize_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            for key in DEFAULT_CONFIG:
                if line.startswith(f"{key} ="):
                    value = line.split("=", 1)[1].strip().strip('"')
                    config[key] = value
    return config


def emit(payload: dict) -> int:
    print(json.dumps(payload))
    return 0


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    prompt = (payload.get("prompt") or "").strip()

    if not prompt:
        return 0

    config = resolve_agent_config()
    cmd = [
        sys.executable,
        str(VALIDATE_SCRIPT),
        "--prompt", prompt,
        "--base-url", config.get("base_url", DEFAULT_CONFIG["base_url"]),
        "--timeout", "8",
    ]
    if config.get("api_key"):
        cmd += ["--api-key", config["api_key"]]
    if config.get("downstream_model"):
        cmd += ["--model", config["downstream_model"]]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        result = json.loads(proc.stdout)
    except Exception as exc:
        result = {"result": "unreachable", "error": str(exc)}

    outcome = result.get("result")
    if outcome in ("unreachable", "http_error"):
        return emit({
            "systemMessage": f"[Marshal] PromptGateway check skipped ({outcome}) -- proceeding without screening. Start PromptGateway to re-enable this check.",
        })

    decision = result.get("decision")
    risk_score = result.get("risk_score")
    reason = result.get("reason", "")
    categories = ", ".join(result.get("categories_triggered", [])) or "none"

    if decision == "BLOCK":
        return emit({
            "decision": "block",
            "reason": f"PromptGateway BLOCK (risk {risk_score}): {reason}. Categories: {categories}",
            "systemMessage": f"[Marshal] BLOCKED (risk {risk_score}): {reason}. Categories: {categories}",
        })

    if decision == "FLAG":
        return emit({
            "systemMessage": f"[Marshal] FLAGGED (risk {risk_score}): {reason}. Categories: {categories}",
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": f"[PromptGateway FLAG] risk_score={risk_score} reason=\"{reason}\" categories={categories}",
            },
        })

    return 0


if __name__ == "__main__":
    sys.exit(main())
