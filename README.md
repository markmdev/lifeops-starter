# LifeOps Starter

A public starter kit that lets Codex install a private, working LifeOps workspace: an Obsidian-compatible vault plus Chief of Staff, Operator, scheduler, source harvesters, action/decision/signal ledgers, knowledge layer, skills, and verification scripts.

## Install

```bash
git clone <this-repo>
cd lifeops-starter
codex
```

Then say:

```text
SETUP LIFEOPS
```

Codex uses `.agents/skills/setup-lifeops/SKILL.md` as an onboarding flow: it explains the operating model, creates a separate private workspace, copies templates and skills, detects available integrations, initializes state, verifies the install, and then walks you through optional activation choices like Operator, source harvesters, private backup, and starring this repo. `SETUP PERSONAL OS` is still accepted as a legacy trigger.

The setup is complete only after the CoS scheduler heartbeat is created and verified in Codex Desktop. If the automation tool is unavailable, the workspace is installed but not fully live; the setup report and action ledger will say exactly what remains unavailable and how to enable it.

## What Gets Installed

- `AGENTS.md`, `SOUL.md`, `DOCS_INDEX.md`, `DOCS_INDEX.full.md`
- `vault/Notes and Journal.md` as the daily cockpit
- `vault/Backlog.md` as readable unresolved work
- `vault/Operations/` with ledgers, queues, schedules, logs, worker prompts, and machine checkpoints
- `vault/Knowledge/` with raw-first source ingestion conventions
- `.agents/skills/` with copied durable skills
- `scripts/` for indexing, linting, backlog rendering, operations validation, scheduler dry runs, privacy scanning, and integration health checks

The packaged operating doctrine is intentionally close to the live LifeOps: full Chief of Staff responsibilities, Calendar control policy, Knowledge I/O, source-adapter signal lifecycle, Operator boundaries, heartbeat setup, and backlog visibility are installed as first-class files rather than summarized in the README.

## Publish Safety

```bash
make test
make e2e-minimal
make privacy
find . -type l -print
```

All checks should pass and `find . -type l -print` should print nothing.
