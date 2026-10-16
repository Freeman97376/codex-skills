"""Local CLI adapters. No API key copying, login mutation, or automatic retries."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid


class BridgeError(RuntimeError):
    pass


def discover(provider: str) -> list[str]:
    home = Path.home()
    found = shutil.which(provider + (".exe" if os.name == "nt" else ""))
    if found and Path(found).suffix.lower() not in {".cmd", ".bat", ".ps1"}:
        return [found]
    if provider == "codex":
        npm = Path(os.environ.get("APPDATA", str(home))) / "npm/node_modules/@openai/codex"
        matches = list(npm.glob("node_modules/@openai/codex-*/vendor/*/bin/codex.exe"))
        if matches:
            return [str(sorted(matches)[-1])]
        node = shutil.which("node")
        if node and (npm / "bin/codex.js").is_file():
            return [node, str(npm / "bin/codex.js")]
    if provider == "claude":
        native = home / ".local/bin" / ("claude.exe" if os.name == "nt" else "claude")
        if native.is_file():
            return [str(native)]
        matches = []
        for editor in (".vscode", ".cursor"):
            matches.extend((home / editor / "extensions").glob(
                "anthropic.claude-code-*/resources/native-binary/claude.exe"))
        def version(path):
            match = re.search(r"claude-code-(\d+)\.(\d+)\.(\d+)", str(path))
            return tuple(map(int, match.groups())) if match else (0, 0, 0)
        if matches:
            return [str(max(matches, key=version))]
    raise BridgeError(f"{provider} CLI not found; configure a local installation first.")


def short_call(argv, timeout=15):
    try:
        result = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True,
                                encoding="utf-8", errors="replace", timeout=timeout,
                                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        return result.returncode, result.stdout, result.stderr
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BridgeError(f"CLI preflight failed: {type(exc).__name__}") from exc


def preflight(provider):
    command = discover(provider)
    code, version, _ = short_call(command + ["--version"])
    if code:
        raise BridgeError(f"{provider} --version failed")
    auth_args = ["login", "status"] if provider == "codex" else ["auth", "status"]
    code, out, err = short_call(command + auth_args)
    if provider == "codex":
        text = out + err
        method = "subscription" if "ChatGPT" in text else (
            "api" if "API key" in text else "unknown")
        auth = {"logged_in": code == 0, "billing": method}
    else:
        try:
            data = json.loads(out)
        except ValueError:
            data = {}
        method = data.get("authMethod")
        auth = {"logged_in": data.get("loggedIn") is True,
                "billing": "subscription" if method == "claude.ai" else (
                    "api" if method in {"api_key", "apiKey", "console"} else "unknown"),
                "subscription_type": data.get("subscriptionType")}
    keys = (("OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL") if provider == "codex" else
            ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
             "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY"))
    overrides = [key for key in keys if os.environ.get(key)]
    return {"provider": provider, "command": command, "version": version.strip(),
            "auth": auth, "environment_overrides_present": overrides,
            "model_availability": "not_verified_no_model_call"}


def check_billing(provider, selection, info):
    if not info["auth"]["logged_in"]:
        raise BridgeError(f"{provider} is not logged in")
    # An inherited key/gateway must never turn subscription intent into another billing route.
    if info["environment_overrides_present"]:
        raise BridgeError(f"{provider} has auth/provider environment overrides; resolve explicitly first")
    if info["auth"]["billing"] != selection["billing"]:
        raise BridgeError(f"{provider} billing route differs from confirmed configuration")
    if provider == "claude" and "fable" in selection["model"].lower():
        if not selection["extra_usage_allowed"]:
            raise BridgeError("Fable can bill usage credits without a print-mode prompt; explicit extra-usage approval required")


def build_command(provider, executable, selection, folder, schema, session=None, reader=None):
    folder = Path(folder)
    if reader and provider != "claude":
        raise BridgeError("Restricted reading currently supports only the Claude reviewer")
    if provider == "claude":
        settings = folder / "settings.json"
        settings.write_text(json.dumps({"disableAllHooks": True, **(
            {"autoMemoryEnabled": False, "claudeMdExcludes": ["**"], "enabledPlugins": {}}
            if reader else {})}), encoding="utf-8")
        mcp = folder / "mcp.json"
        mcp.write_text(json.dumps({"mcpServers": reader["servers"] if reader else {}}), encoding="utf-8")
        command = executable + [
            "-p", "--model", selection["model"], "--effort", selection["effort"],
            "--output-format", "json", "--json-schema", json.dumps(schema, separators=(",", ":")),
            "--restricted", "--tools", "",
            "--permission-mode", "dontAsk", "--permission-prompts", "none",
            "--strict-mcp-config", "--mcp-config", str(mcp),
            "--settings", str(settings), "--disable-slash-commands",
            "--no-chrome"]
        if reader:
            command += ["--allowedTools", *reader.get("tools", ["mcp__review_packet__read_source"]), "--setting-sources", "",
                        "--max-turns", str(reader["max_turns"])]
        else:
            command += ["--safe-mode", "--disallowedTools", "mcp__*"]
        if session is None:
            command += ["--no-session-persistence"]
        else:
            command += ["--session-id", session["id"], "--name", session["name"]]
        return command
    schema_path = folder / "schema.json"
    schema_path.write_text(json.dumps(schema), encoding="utf-8")
    command = executable + [
        "exec", "--ignore-user-config", "--sandbox", "read-only", "--ephemeral",
        "--skip-git-repo-check", "--cd", str(folder), "--model", selection["model"],
        "--config", 'model_reasoning_effort="' + selection["effort"] + '"',
        "--config", 'approval_policy="never"', "--config", 'web_search="disabled"',
        "--config", "project_doc_max_bytes=0",
        "--output-schema", str(schema_path), "--json",
        "--output-last-message", str(folder / "final.json")]
    for feature in ("shell_tool", "unified_exec", "multi_agent", "multi_agent_v2",
                    "plugins", "hooks", "apps", "memories", "skill_search",
                    "browser_use", "browser_use_external", "computer_use",
                    "image_generation", "in_app_browser", "code_mode"):
        command += ["--disable", feature]
    return command + ["-"]


def run_process(argv, cwd, stdin, timeout, max_output=8_000_000):
    """Bounded process execution; raw outputs live only in a temporary directory."""
    if not argv or Path(argv[0]).suffix.lower() in {".cmd", ".bat", ".ps1"}:
        raise BridgeError("Use a native executable or explicit Python/Node/PowerShell interpreter, not a shell shim")
    with tempfile.TemporaryDirectory(prefix="collab-process-") as temporary:
        temp = Path(temporary)
        started = time.monotonic()
        env = os.environ.copy()
        # Avoid creating a nested interactive Claude session or a background updater.
        env.pop("CLAUDECODE", None)
        env["DISABLE_AUTOUPDATER"] = "1"
        flags = (subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP) if os.name == "nt" else 0
        with (temp / "input").open("wb") as input_file:
            input_file.write(stdin.encode("utf-8"))
        with (temp / "input").open("rb") as input_file, (temp / "out").open("wb") as out, (temp / "err").open("wb") as err:
            process = subprocess.Popen(argv, cwd=cwd, env=env, stdin=input_file, stdout=out, stderr=err,
                                       creationflags=flags, start_new_session=os.name != "nt")
            try:
                while process.poll() is None:
                    if time.monotonic() - started > timeout:
                        raise BridgeError("Process timed out; no automatic retry")
                    if (temp / "out").stat().st_size + (temp / "err").stat().st_size > max_output:
                        raise BridgeError("Process output exceeded limit; no automatic retry")
                    time.sleep(0.1)
            finally:
                if process.poll() is None:
                    if os.name == "nt":
                        subprocess.run(["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
                                       capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    else:
                        os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=10)
        output = (temp / "out").read_bytes()
        error = (temp / "err").read_bytes()
        if len(output) + len(error) > max_output:
            raise BridgeError("Process output exceeded limit")
        return {"returncode": process.returncode,
                "stdout": output.decode("utf-8", errors="replace"),
                "stderr": error.decode("utf-8", errors="replace"),
                "duration_seconds": round(time.monotonic() - started, 3)}


def parse_output(provider, result, folder):
    if result["returncode"]:
        raise BridgeError(f"{provider} process failed (exit {result['returncode']}); raw logs are not persisted")
    models = set()
    usage = {}
    if provider == "claude":
        try:
            data = json.loads(result["stdout"])
        except ValueError as exc:
            raise BridgeError("Claude output was not JSON") from exc
        if not isinstance(data, dict) or data.get("is_error") or data.get("type") != "result" or data.get("subtype") != "success":
            raise BridgeError("Claude did not return a successful result")
        model_usage = data.get("modelUsage", {})
        token_usage = data.get("usage", {})
        if not isinstance(model_usage, dict) or not isinstance(token_usage, dict) or any(not isinstance(m, str) for m in model_usage):
            raise BridgeError("Claude returned invalid usage metadata")
        models.update(model_usage.keys())
        report = data.get("structured_output")
        if report is None:
            try:
                report = json.loads(data.get("result", ""))
            except (TypeError, ValueError) as exc:
                raise BridgeError("Claude returned no structured report") from exc
        usage = {key: value for key, value in token_usage.items()
                 if key in {"input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"}}
        cache_creation = token_usage.get("cache_creation")
        if isinstance(cache_creation, dict):
            usage["cache_creation"] = {key: value for key, value in cache_creation.items()
                                       if key in {"ephemeral_5m_input_tokens", "ephemeral_1h_input_tokens"}
                                       and type(value) is int and value >= 0}
    else:
        completed = False
        for line in result["stdout"].splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if not isinstance(event, dict):
                raise BridgeError("Codex returned an invalid event envelope")
            if event.get("type") in {"turn.failed", "error"}:
                raise BridgeError("Codex emitted a failure event")
            if event.get("type") == "turn.completed":
                completed = True
                usage = event.get("usage", {})
                if not isinstance(usage, dict):
                    raise BridgeError("Codex returned invalid usage metadata")
            # Only provider metadata, never model-authored prose, verifies model identity.
            if event.get("type") in {"session.started", "session.updated", "response.completed", "turn.completed"}:
                response = event.get("response", {})
                if not isinstance(response, dict):
                    raise BridgeError("Codex returned invalid response metadata")
                model = event.get("model") or response.get("model")
                if isinstance(model, str):
                    models.add(model)
        if not completed:
            raise BridgeError("Codex emitted no completed turn")
        try:
            report = json.loads((Path(folder) / "final.json").read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise BridgeError("Codex returned no structured report") from exc
    return report, {"actual_models": sorted(models), "usage": usage,
                    "duration_seconds": result["duration_seconds"]}


def invoke(provider, selection, prompt, schema, timeout, read_bundle=None):
    if read_bundle is not None and provider != "claude":
        raise BridgeError("Restricted reading currently supports only the Claude reviewer")
    info = preflight(provider)
    check_billing(provider, selection, info)
    session = None
    config = None
    read_audit = None
    if provider == "claude":
        if os.environ.get("CLAUDE_CODE_SKIP_PROMPT_HISTORY", "").lower() in {"1", "true"}:
            raise BridgeError("Claude history is disabled by CLAUDE_CODE_SKIP_PROMPT_HISTORY; resolve explicitly before a saved review")
        config = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude").expanduser().resolve()
        session_id = str(uuid.uuid4())
        session = {"id": session_id, "name": "C-C review " + time.strftime("%Y-%m-%d %H-%M-%S") + " " + session_id[:8],
                   "cwd": str(config / "collaboration-reviews"),
                   "resume_argv": info["command"] + ["--resume", session_id],
                   "persistence": "requested", "picker_visibility": "print sessions require explicit resume by ID"}
    try:
        if session:
            Path(session["cwd"]).mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="codex-claude-review-") as temporary:
            reader = None
            if read_bundle is not None:
                import restricted_read
                # Safe mode disables all MCP; bare mode changes subscription auth. Neither is used here.
                if any(os.environ.get(key, '').lower() in {'1', 'true'} for key in
                       ('CLAUDE_CODE_SAFE_MODE', 'CLAUDE_CODE_SIMPLE')):
                    raise BridgeError("Inherited Claude mode conflicts with restricted reading")
                bundle_path = Path(temporary) / 'frozen.json'
                bundle_path.write_text(restricted_read.encode(read_bundle), encoding='utf-8')
                audit_path = Path(temporary) / 'reads.json'
                reader = {'servers': {'review_packet': {'type': 'stdio', 'command': sys.executable,
                    'args': ['-X', 'utf8', str(Path(__file__).with_name('restricted_read.py').resolve()),
                             str(bundle_path), restricted_read.fingerprint(read_bundle), str(audit_path)]}},
                          'max_turns': read_bundle['limits']['max_turns'],
                          'tools': ['mcp__review_packet__read_source'] + (
                              ['mcp__review_packet__search_sources'] if read_bundle.get('mode') == 'project' else [])}
            command = build_command(provider, info["command"], selection, temporary, schema, session=session, reader=reader)
            try:
                result = run_process(command, session["cwd"] if session else temporary, prompt, timeout)
                report, metadata = parse_output(provider, result, temporary)
            finally:
                if reader:
                    try:
                        read_audit = json.loads(audit_path.read_text(encoding='utf-8'))
                    except (OSError, ValueError):
                        read_audit = {'status': 'unavailable'}
            if reader:
                restricted_read.verify_audit(read_bundle, read_audit)
                metadata['restricted_read'] = read_audit
        actual = metadata["actual_models"]
        if actual and any(model != selection["model"] for model in actual):
            raise BridgeError(f"Model mismatch: requested {selection['model']}, reported {', '.join(actual)}")
        metadata.update({"requested_model": selection["model"],
                         "model_verification": "verified" if actual else "unavailable",
                         "cli_version": info["version"], "billing_route": info["auth"]["billing"]})
        if session:
            metadata["claude_session"] = session
        return report, metadata
    except (BridgeError, OSError, ValueError, TypeError, KeyError) as exc:
        if session:
            exc.claude_session = session
        if read_audit is not None:
            exc.restricted_read = read_audit
        raise
    finally:
        # Inspect only this invocation's transcript; never copy other conversations.
        if session:
            try:
                paths = list((config / "projects").glob("*/" + session["id"] + ".jsonl"))
                paths = [path for path in paths if path.is_file() and path.stat().st_size > 0]
            except OSError:
                paths = []
            session["persistence"] = "saved" if len(paths) == 1 else "not_verified"
            if len(paths) == 1:
                session["transcript_path"] = str(paths[0])
