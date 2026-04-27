# LifeOps Starter Repo Instructions

This is a public starter repository for installing a private LifeOps workspace. The repo itself contains templates, the setup skill/scripts, and verification tests only. It must not contain private user state, live vault files, logs, action ledgers, decision queues, message/email content, calendar data, screenshots, PDFs, credentials, browser profiles, or machine-specific private paths.

## Primary Command

When the user says `SETUP LIFEOPS` or `SETUP PERSONAL OS`, immediately use `$setup-lifeops`. If skill invocation is unavailable, read and follow `.agents/skills/setup-lifeops/SKILL.md`.

## Required Behavior

The setup must create a separate private workspace outside this starter repo, copy templates and skills into it without symlinks, render parameterized files, initialize an Obsidian-compatible vault, initialize `vault/Operations/` state, install the core Chief of Staff, Operator, scheduler, harvester, communication, and knowledge skills, actively detect and help enable integrations, write setup reports, run privacy checks before backup, and never push private data to a public repository.

## Public Repo Safety

Do not write live ledgers, logs, outboxes, `.machine` state, Gmail links, message IDs, calendar links, private PDFs/screenshots, `.DS_Store`, `__pycache__`, tokens, cookies, OAuth files, `.env` files, or absolute private paths into this repo.

## Development Checks

```bash
make test
make privacy
find . -type l -print
```
