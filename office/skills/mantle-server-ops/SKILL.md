---
name: mantle-server-ops
description: Inspect or deploy the Mantle server, including the saved aliases moi serever, moi server, and tencent cloud 1, for systemd status, resource checks, upload/auth diagnosis, subdirectory routing, or the deploy-mantle flow. Specific to Mantle rather than general server deployment.
---

# mantle-server-ops

## When to use

- Use in `C:/path/to/mantle_of_intelligence2.0` for live-server deployment, restart, upload/auth debugging, or server-state reporting.
- Use when the user wants exact server commands or only the next operational step.
- Do not use for local-only Windows startup, offline code review, or doc-only `office/` edits.

## Inputs / context to gather

1. Confirm the repo is the inner `...\mantle_of_intelligence2.0` checkout. If it has moved, resolve the current project root.
2. Confirm whether the task is:
   - deploy/update
   - runtime failure diagnosis
   - upload/auth/path verification
   - server resource/status report
3. Use these recorded identifiers as starting points; verify them against the current repo and service configuration before acting:
   - `example-app.service`
   - app direct health `http://127.0.0.1:8001/health`
   - public path `https://example.com/bid-system/`
   - server app dir `/opt/projects/example-app`
   - The public domain and base path are user-controlled; do not replace a current user-specified value with these historical defaults.
4. If the user mentions uploads or auth, inspect the frontend/backend contract points:
   - `frontend/assets/upload-reliability.js`
   - `app/api/routes/files.py`
   - `app/security/auth.py`
   - `app/api/routes/auth.py`
5. If the user mentions deployment or restart, check whether `scripts/deploy_server.sh` is present and whether the server is already on the target commit.
6. Resolve the saved local connection below before asking for an SSH address or key path. Establish whether the user wants direct operation or commands to run themselves. A saved profile identifies the connection; it does not expand the user's requested scope or authorize a deployment.

## Saved local connections

Read [.local/connections.json](.local/connections.json) from this skill's own directory before a server connection task. Resolve this path relative to `SKILL.md`, including when invoked through the personal skill junction, not relative to the project working directory.

- The JSON file has `schema_version: 1`, a `default_connection` ID, and a `connections` list. Each connection contains `id`, `aliases`, an `ssh` object (`host`, `username`, `port`, `identity_file`), and `expected_hostname`.
- Match the requested connection ID or alias after trimming, collapsing repeated whitespace, and ignoring case. Preserve the user-provided spelling `moi serever`; `moi server` and `tencent cloud 1` are equivalent aliases. For a Mantle task without a named target, use `default_connection`. An unknown or ambiguous alias requires clarification; never silently select another server. Current explicit user connection details take precedence over saved values.
- Parse this file as data (`Get-Content -LiteralPath <profile-path> -Raw | ConvertFrom-Json` on PowerShell). Do not evaluate profile values as shell code. Check that the selected identity file exists; inspect `ssh-add -l` when agent readiness matters. A missing user SSH `config` file does not mean the saved key or connection is unavailable. Do not ask the user to resend values already present in the profile.
- Build SSH arguments from `ssh.username`, `ssh.host`, `ssh.port`, and `ssh.identity_file`, passing each argument separately. Use `-o BatchMode=yes -o StrictHostKeyChecking=yes -o IdentitiesOnly=yes -o ConnectTimeout=10 -o ConnectionAttempts=1`, plus `-p` and `-i`. Keep host-key verification enabled. Report a missing file, authentication failure, unknown/changed host key, or timeout specifically; do not search unrelated keys or weaken verification to make a connection succeed.
- On an authorized connection, verify the remote user and hostname, then inspect the current service and working directory. Compare the hostname with `expected_hostname` and reconcile differences before changes. Follow the task's requested scope: status checks remain read-only; deployment, restart, or configuration changes require the user's corresponding request.
- Keep connection addresses, usernames, and identity paths in the local profile rather than this entrypoint, UI metadata, examples, or shared records. The profile stores a reference to an existing private key, never private-key bytes or passwords. Keep `.local/` out of commits and any exported skill package; `.gitignore` covers Git, while manual packaging must explicitly omit it. Report aliases by default and show connection details only when needed or requested.

## Procedure

1. Start with the live service, not `nohup`.
   - Check `sudo systemctl status example-app --no-pager`
   - Check `sudo systemctl cat example-app`
   - Check `sudo journalctl -u example-app -n 200 --no-pager -o short-iso`
2. If the task is upload/auth/runtime diagnosis, inspect the request path and proxy layer next.
   - Inspect a bounded recent log sample, such as `sudo tail -n 200 /var/log/nginx/error.log /var/log/nginx/access.log`; use `tail -F` only for a requested live observation with a clear stopping point.
   - Search the exact endpoint, for example `POST /api/sessions/.../upload`.
3. Verify the three health layers separately, using the confirmed current addresses:
   - direct app: `http://127.0.0.1:8001/health`
   - local proxied path: `/bid-system/health`
   - public HTTPS: `https://example.com/bid-system/health`
4. For auth verification, prove both public and protected behavior. Recheck the current server auth contract against the recorded expectations:
   - `/health` should stay public
   - `/api/auth/status` should show `auth_required:true`
   - `/api/sessions`, `/docs`, and `/openapi.json` should return `401 authentication_required` without credentials
5. For authorized deploy/update work:
   - Inspect and prefer `scripts/deploy_server.sh` / `deploy-mantle` if the script exists
   - Stop if tracked files are dirty; preserve the server's edits
   - Back up `.env` and DB state without exposing credentials in output or records
   - Keep the update fast-forward only
   - Restart the confirmed `example-app.service`
   - Verify the relevant health layers after restart
6. For resource/status requests, gather:
   - `df -h`
   - `free -h`
   - `sudo ss -lntp`
   - `sudo ufw status numbered`
   - `git log -1 --oneline`
   - `alembic current`

## Efficiency plan

- Treat `systemd` as the source of truth first; this avoids wasting time on ad hoc process state.
- Separate direct app health, local Nginx routing, and public HTTPS checks so failures localize quickly.
- When the user asks for ops help, answer with the next concrete command or short sequence instead of a long checklist.
- Reuse `scripts/deploy_server.sh` when present instead of inventing a fresh deployment flow.

## Pitfalls and fixes

- Symptom: restart appears to work but old behavior remains. Likely cause: the wrong process was checked or `nohup` was mixed with `systemd`. Fix: inspect `systemctl status`, `systemctl cat`, and `journalctl` first.
- Symptom: subdirectory verification fails after TLS is enabled. Likely cause: the check still uses HTTP or ignores redirects. Fix: verify the final HTTPS URL or use a local `--resolve` check against the public host.
- Symptom: uploads show generic failure but no parse exception appears. Likely cause: the frontend collapsed auth/proxy/response-shape failures into `upload failed`. Fix: separate request acceptance, parse status, and later file/API access errors.
- Symptom: protected APIs return `401`, but the deployment is still insecure. Possible cause: an old public `8081` HTTP path remains open. Verify current exposure; treat probe blocking and transport security as separate checks.
- Symptom: a deploy script would overwrite server edits. Likely cause: it ignores tracked-file drift. Fix: fail on dirty tracked files and never use `git reset --hard`.

## Verification checklist

- Confirmed the inner repo root and the relevant live-server mode.
- Checked the current service identity and state before deeper diagnosis.
- Verified direct app, proxied path, and public HTTPS at the correct layer for the task.
- If auth was in scope, confirmed both public routes and protected-route behavior against the current contract.
- If deploy was in scope, confirmed the script or command path avoided dirty-file overwrite and used `systemd`.
- Final report gives exact commands, concrete status, and the remaining risk or next step; distinguish user-run commands from checks actually executed.
