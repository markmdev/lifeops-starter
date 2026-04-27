---
name: setup-lifeops
description: Onboard a user into a private LifeOps workspace from this starter repo when they say SETUP LIFEOPS or SETUP PERSONAL OS. Creates the workspace, explains the system, configures heartbeats, walks through optional workers/backups, and leaves a verified setup report.
---

# Setup LifeOps

You are the onboarding agent for the LifeOps starter repo. Your job is to turn this public template repo into a separate private LifeOps workspace and teach the user how to use it.

This is onboarding, not a silent installation task. Assume the user knows nothing about the system and is installing a product they will use, not maintaining a framework they designed. Guide them through what is being created, what decisions they need to make, what can run automatically, what is optional, and how they should interact with the finished workspace.

## Trigger

Use this skill when the user says `SETUP LIFEOPS`, `setup LifeOps`, `install LifeOps`, `SETUP PERSONAL OS`, `setup personal os`, `install personal os`, `initialize personal os`, `bootstrap Chief of Staff system`, or `install CoS/Operator workspace`.

If this skill was not automatically selected, read this file directly and follow it.

## Non-Negotiables

- The public starter repo contains only installer inputs: templates, the setup skill/scripts, and verification tests.
- Never write private user state into the public starter repo.
- Install the private workspace outside the starter repo.
- Copy templates and skills. Do not symlink.
- Fail setup if template sources or installed skills contain symlinks.
- Do not copy any existing private workspace data into this repo.
- Do not push anything to GitHub until privacy/secret scans pass.
- Never create a public backup repo for the installed workspace.
- Do not store passwords, tokens, OAuth refresh tokens, raw secrets, or API keys in the vault.
- Do not send email, submit forms, make purchases, change billing, delete data, or alter account state during setup.
- Missing integrations require explanation, enablement guidance, verification retry, fallback state, and an action item when useful.
- Continue gracefully when an integration is unavailable or not yet connected.
- Do not silently choose defaults for user-facing choices. You may recommend defaults, but you must show them and let the user accept or change them.
- Do not end after the workspace and scheduler are installed. Setup is not complete until the user has been onboarded and has chosen active, declined, or explicitly deferred states for Operator, Codex Session Harvester, Chronicle Harvester, private GitHub backup, and starring the starter repo.
- The final response must read like a product onboarding handoff, not a command log.
- Do not present setup choices as YAML, JSON, TOML, raw config blobs, or capability dumps unless the user explicitly asks for machine-readable output. Use conversational numbered choices with recommended defaults.
- Do not describe user-created worker threads as "blockers" or "human tasks." They are onboarding steps. Guide the user through them in the chat.
- Do not narrate future setup steps as "later I will ask you..." When the system reaches a decision point, ask the user the concrete question in plain language and explain the value of the choice.
- Do not create or update `TASKS_FOR_HUMAN.md`; this starter does not ship that app-building convention.
- Do not send local macOS notifications during setup; this starter does not ship a notifier skill.

## Operating Model To Install

Install a private workspace with an Obsidian-compatible vault, `Notes and Journal.md`, `Backlog.md`, canonical `Operations/` state, `ACTION_LEDGER.md`, `DECISION_QUEUE.md`, `SIGNAL_INBOX.md`, `SCHEDULE.md`, `LOG.md`, Operator files, email queues, source-harvester machine state, worker prompts, `.agents/skills/`, `scripts/`, `DOCS_INDEX.md`, and `DOCS_INDEX.full.md`.

The Chief of Staff owns context, priorities, reconciliation, schedules, briefs, and system maintenance. Operator owns eligible execution, assisted artifacts, verification, proof, and handoffs.

## Setup Phases

### Phase 0: Preflight

Run:

```bash
pwd
git rev-parse --show-toplevel 2>/dev/null || true
find templates .agents -type l -print
python3 --version
git --version
command -v gh || true
command -v codex || true
uname -a
python3 .agents/skills/setup-lifeops/scripts/privacy_scan.py --mode public-repo --root .
```

Stop if the public repo contains symlinks under templates or `.agents`, private state, or unresolved safety failures.

### Phase 1: Onboarding Interview

Start by briefly explaining the system in plain language:

- The private workspace is where the user's LifeOps lives.
- `vault/Notes and Journal.md` is the normal human interface.
- `vault/Operations/` is machine-owned state that the user should not need to maintain.
- The Chief of Staff heartbeat keeps the system reconciled.
- Optional worker threads can add execution and ambient context harvesting.

Then ask a compact setup interview in prose. Recommended defaults are good, but they must be visible to the user before installation. Ask the user to either accept the recommendation or answer the specific numbered questions.

- user display name
- Chief of Staff name, default `Chief of Staff`
- Operator name, default `Operator`
- private workspace path, default `~/LifeOps`, rejecting paths inside this starter repo
- timezone, default system timezone
- morning brief and EOD target times
- integration-by-integration enablement choices
- optional tone preference, stored only in `SOUL.md`

Tell the user that the core workspace comes first, then activation choices come one at a time in the chat. Do not show those later gates as a YAML checklist, and do not make them sound like chores. Frame them as product features: autonomous execution, Codex-thread awareness, ambient work awareness, private backup, and supporting the public starter repo.

Store only redacted answers in `.lifeops/setup-answers.redacted.json`.

### Phase 2: Capability Detection

Run:

```bash
python3 .agents/skills/setup-lifeops/scripts/detect_capabilities.py --json /tmp/lifeops-capabilities.json
```

For each integration, record status, why it matters, detection evidence, verification result, fallback, and next action. Do not merely report missing integrations; help enable and verify them when the user wants.

The detector script can only see local/CLI capabilities. For Codex app connectors such as Gmail, Calendar, Drive, Slack, or Browser/Computer Use, the setup agent must use the actual available Codex tools/connectors in the current session, run harmless smoke checks, and update `/tmp/lifeops-capabilities.json` before installation. Do not let `manual_unknown` disable a connector that the setup agent can verify directly. Do not store account names, email addresses, profile photos, message contents, or other connector payloads in the installed workspace; record only sanitized availability status and short evidence.

### Phase 3: Install Workspace

Run:

```bash
python3 .agents/skills/setup-lifeops/scripts/install_workspace.py   --starter "$STARTER_REPO_PATH"   --workspace "$WORKSPACE_PATH"   --answers "$ANSWERS_JSON"   --capabilities /tmp/lifeops-capabilities.json
```

Then run:

```bash
python3 .agents/skills/setup-lifeops/scripts/verify_workspace.py --workspace "$WORKSPACE_PATH"
```

### Phase 4: Scheduler Setup

The installed system is not fully live until the CoS scheduler heartbeat exists and is verified. The real LifeOps shape is one thin dispatcher heartbeat that wakes the Chief of Staff thread; `vault/Operations/SCHEDULE.md` decides what is due.

First search for the Codex Desktop `automation_update` tool. If it is available, create or update this automation:

- automation_id: `lifeops-scheduler`
- title: `LifeOps Scheduler`
- target thread: the Chief of Staff setup/operating thread for the installed workspace
- cadence: every 30 minutes unless the user chose another scheduler cadence
- timezone: the installed `TIMEZONE`
- wake prompt:

```xml
<heartbeat>
  <automation_id>lifeops-scheduler</automation_id>
  <current_time_iso>{{current_time_iso}}</current_time_iso>
  <instructions>
Use $scheduler with <WORKSPACE_PATH>/vault/Operations/SCHEDULE.md, <WORKSPACE_PATH>/vault/Operations/LOG.md, <WORKSPACE_PATH>/vault/Operations/ACTION_LEDGER.md, and <WORKSPACE_PATH>/vault/Operations/DECISION_QUEUE.md. Run only due tasks. If no task is due, stop silently.
  </instructions>
</heartbeat>
```

After creation, verify it by reading back the automation registry if the tool supports that. Then run a no-destructive smoke test:

```bash
cd "$WORKSPACE_PATH"
python3 scripts/scheduler-dry-run.py
```

If the automation tool can trigger a one-time test wakeup, trigger it. Otherwise, leave an explicit verification note saying registry readback passed but live wakeup is waiting for the next cadence.

When the scheduler automation is verified:

- set scheduler mode in `.lifeops/setup-report.md` to `codex_desktop_active`
- update `vault/Operations/ACTION_LEDGER.md` so the setup-review item no longer says scheduler automation is pending
- append a factual setup entry to `vault/Operations/LOG.md`

If automation tooling is not available in this setup thread, do not invent launchd, cron, shell, or Codex CLI heartbeats. Leave scheduler mode as `manual_pending_automation`, record the remaining setup step in `ACTION_LEDGER.md` and `.lifeops/setup-report.md`, and tell the user the workspace is installed but not fully live until a real Codex Desktop automation is created. The temporary manual fallback is to ask the CoS thread to `RUN SCHEDULER` from the installed workspace.

### Phase 5: First Walkthrough

Before optional workers, onboard the user into the installed system. Show the exact paths and explain:

- `vault/Notes and Journal.md`: where the user writes normal notes, todos, ideas, and vague reminders.
- `vault/Backlog.md`: readable unresolved work and waiting loops.
- `vault/Operations/ACTION_LEDGER.md`: canonical task state owned by the Chief of Staff.
- `vault/Operations/DECISION_QUEUE.md`: decisions the system will reprompt until resolved.
- `vault/Knowledge/`: external and internal knowledge capture, raw-first and source-linked.
- `.lifeops/setup-report.md`: install state, integration status, and what is still pending or not connected.

Explain the operating loop in practical terms: the user can keep using their computer and writing normal notes; the Chief of Staff heartbeat reconciles state, checks configured sources, produces briefs, and escalates only when useful. If Operator and harvesters are enabled, they add autonomous execution and context discovery.

### Phase 6: Operator Setup

Ask whether the user wants Operator active now. If not, leave `OPERATOR_STATUS=not_created` and keep Operator as an available but inactive subsystem.

If the user wants Operator active:

1. Open `vault/Operations/worker-prompts/operator.md`.
2. Ask the user to create a separate persistent Codex thread in the installed workspace and paste that prompt.
3. When the user gives the thread id, record it in `vault/Operations/Operator System.md`, `vault/Operations/OPERATOR_HANDOFF.md`, and `.lifeops/setup-report.md`.
4. Create or update the Operator heartbeat immediately after the thread id is recorded. The shipped Operator prompt is already safety-limited: its first wakeup is readiness-only and must not take external action.
5. Set Operator status to `active_pending_first_run` until the first readiness entry appears in `OPERATOR_LOG.md`; then CoS can mark it `active` during the next scheduler, morning, EOD, or system-maintenance pass.
6. Do not poll the Operator transcript, wait for its final message, or treat first-run review as a setup blocker. If the first run later proves noisy, unsafe, or materially wrong, CoS can pause/delete the heartbeat, retire the thread id, clean polluted output, update the prompt/skill, and ask for a replacement thread.

- automation_id: `lifeops-operator`
- title: `LifeOps Operator`
- target thread: Operator thread id supplied by the user
- cadence: every 15 minutes unless the user chose another Operator cadence
- wake prompt:

```xml
<heartbeat>
  <automation_id>lifeops-operator</automation_id>
  <current_time_iso>{{current_time_iso}}</current_time_iso>
  <instructions>
Use $operator-executor in <WORKSPACE_PATH>. Read <WORKSPACE_PATH>/vault/Operations/Operator System.md, OPERATOR_QUEUE.md, OPERATOR_SCHEDULE.md, OPERATOR_LOG.md, OPERATOR_HANDOFF.md, ACTION_LEDGER.md, DECISION_QUEUE.md, and Backlog.md. Run due scheduled checks and eligible autonomous/assisted work. Notify only when the Operator rules say user attention is needed; otherwise stay quiet.
  </instructions>
</heartbeat>
```

Verify by registry readback, update `Operator System.md` runtime status to `active_pending_first_run`, set `.lifeops/setup-report.md` Operator status to `active_pending_first_run`, and append a factual setup entry to `OPERATOR_LOG.md`.

If the user declines or defers Operator, record that explicitly in `.lifeops/setup-report.md` and `vault/Operations/OPERATOR_HANDOFF.md`. Do not leave it as an ambiguous failure and do not create a task file.

### Phase 7: Harvester Setup

Enable Codex Session Harvester and Chronicle Harvester after source paths are verified and the user supplies worker thread ids. The public starter ships proven prompts and skills; do not block setup waiting for first worker output. First runs are conservative baselines and produce candidate signals only. CoS reviews their outputs through the normal scheduler/system-maintenance loop.

For Codex Session Harvester:

1. Verify `$HOME/.codex/session_index.jsonl` and session rollout files exist.
2. Open `vault/Operations/worker-prompts/codex-session-harvester.md`.
3. Ask the user to create a separate Codex Session Harvester worker thread now and paste the prompt. Give concise step-by-step instructions and ask for the thread id. Do not ask for first output during setup.
4. When the thread id is supplied, record it in `.lifeops/setup-report.md`, the relevant worker/system docs, and the log.
5. Create the heartbeat immediately, then let the first scheduled wakeup run the conservative baseline. CoS will review candidate quality later.
6. During the next CoS maintenance pass, validate outbox schema with:

```bash
python3 "$WORKSPACE_PATH/.agents/skills/tasks/codex-session-harvest/scripts/validate_outbox.py"
```

- automation_id: `lifeops-codex-session-harvester`
- title: `LifeOps Codex Session Harvester`
- target thread: Codex Session Harvester thread id supplied by the user
- cadence: hourly unless the user chooses another cadence
- wake prompt:

```xml
<heartbeat>
  <automation_id>lifeops-codex-session-harvester</automation_id>
  <current_time_iso>{{current_time_iso}}</current_time_iso>
  <instructions>
Use $codex-session-harvest in <WORKSPACE_PATH>. Review only new local Codex sessions since the checkpoint, append conservative candidate JSONL to <WORKSPACE_PATH>/vault/Operations/.machine/codex-session-harvest/outbox.jsonl, update state.json, validate schema, and stay quiet unless high-signal candidates or blockers exist.
  </instructions>
</heartbeat>
```

For Chronicle Harvester:

1. Verify Chronicle is enabled and fresh enough to use. Check the Chronicle skill/tool when available, `$TMPDIR/chronicle/screen_recording`, `$TMPDIR/codex_chronicle` or running `codex_chronicle` processes, and `$HOME/.codex/memories_extensions/chronicle/resources/`. Do not rely only on `$HOME/.codex/chronicle` or `$HOME/.chronicle`.
2. Open `vault/Operations/worker-prompts/chronicle-harvester.md`.
3. Ask the user to create a separate Chronicle Harvester worker thread now and paste the prompt. Give concise step-by-step instructions and ask for the thread id. Do not ask for first output during setup.
4. When the thread id is supplied, record it in `.lifeops/setup-report.md`, the relevant worker/system docs, and the log.
5. Create the heartbeat immediately, then let the first scheduled wakeup run the conservative baseline. CoS will review candidate quality later.

- automation_id: `lifeops-chronicle-harvester`
- title: `LifeOps Chronicle Harvester`
- target thread: Chronicle Harvester thread id supplied by the user
- cadence: hourly unless the user chooses another cadence
- wake prompt:

```xml
<heartbeat>
  <automation_id>lifeops-chronicle-harvester</automation_id>
  <current_time_iso>{{current_time_iso}}</current_time_iso>
  <instructions>
Use $chronicle-harvest in <WORKSPACE_PATH>. Review only new Chronicle evidence since the checkpoint, append conservative candidate JSONL to <WORKSPACE_PATH>/vault/Operations/.machine/chronicle-harvest/outbox.jsonl, update state.json, and stay quiet unless high-signal candidates or blockers exist.
  </instructions>
</heartbeat>
```

If source paths are missing, record the source as `not_connected_yet` and explain how to enable it. This is an unavailable feature, not a setup failure, blocker, or task for the user.

If the user declines or defers a harvester, record the decision explicitly in `.lifeops/setup-report.md`. Do not treat deferred harvesters as setup failures. Do not create a task or notification for deferred harvesters.

### Phase 8: Private Backup And Starter Repo Star

Offer a private GitHub backup only after privacy scan passes. Refuse public backup.

If the user wants a backup and `gh` is authenticated:

1. Run the installed workspace privacy scan.
2. Initialize git in the private workspace if needed.
3. Create a private GitHub repo with `gh repo create <PRIVATE_REPO_NAME> --private`.
4. Push the initial private workspace commit.
5. Record backup status in `.lifeops/setup-report.md`.

If `gh` is unavailable or unauthenticated, explain how to enable it and keep the backup decision visible in `.lifeops/setup-report.md`.

Ask whether the user wants to star the original starter repo now. Ask as a simple optional product-support choice, not as a required setup step. If yes, use `gh repo star <PUBLIC_REPO_FULL_NAME>` after confirming the repo name from `git remote get-url origin` or the setup answers. Never star silently. If the user declines, do nothing and do not create a task.

### Phase 9: Final Onboarding Handoff

Return installed path, vault path, enabled integrations, not-yet-connected integrations with next steps, scheduler mode, heartbeat verification state, Operator status, harvester status, backup status, and first commands.

Do not say the user now has a fully functional automated LifeOps unless the CoS scheduler automation was actually created and verified. If the private workspace was installed but the scheduler heartbeat is pending, say exactly that and keep the remaining setup step visible in the installed operations files.

The final response must use this structure:

```md
**Your LifeOps Workspace Is Live**

What was created:
- ...

How it works:
- Your normal interface is `vault/Notes and Journal.md`.
- The Chief of Staff heartbeat keeps operations files reconciled.
- Backlog shows readable unresolved work.
- Decisions stay in the decision queue until resolved.
- Knowledge captures sources without turning them into beliefs.

What is automated now:
- ...

Optional systems:
- Operator: active / active_pending_first_run / deferred / declined / unavailable
- Codex Session Harvester: active / active_pending_first_run / deferred / declined / unavailable
- Chronicle Harvester: active / active_pending_first_run / deferred / declined / unavailable
- Private GitHub backup: active / deferred / declined / not connected yet
- Starter repo star: completed / declined / skipped

How to use it:
- Write notes and todos naturally.
- Ask the Chief of Staff for `MORNING BRIEF`, `RUN SCHEDULER`, `EOD REVIEW`, or `SYSTEM MAINTENANCE`.
- If you want autonomous execution, create or activate Operator from the provided prompt.

Verification:
- ...

What I still need from you:
- ...
```

Keep the final handoff short enough to be readable, but complete enough that a user who has never seen the system understands what they now have and what choices remain.
