#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path
from common import ensure_no_symlinks, has_unresolved_placeholders
REQUIRED=['AGENTS.md','SOUL.md','README.private.md','DOCS_INDEX.md','DOCS_INDEX.full.md','vault/Notes and Journal.md','vault/Backlog.md','vault/Profile/Profile.md','vault/Immigration/Immigration.md','vault/Operations/ACTION_LEDGER.md','vault/Operations/DECISION_QUEUE.md','vault/Operations/SIGNAL_INBOX.md','vault/Operations/SCHEDULE.md','vault/Operations/LOG.md','vault/Operations/Operator System.md','vault/Operations/OPERATOR_QUEUE.md','vault/Operations/OPERATOR_SCHEDULE.md','vault/Operations/OPERATOR_LOG.md','vault/Operations/OPERATOR_HANDOFF.md','vault/Knowledge/Knowledge.md','vault/Knowledge/INBOX.md','scripts/backlinks.py','.agents/skills/tasks/scheduler/SKILL.md','.agents/skills/tasks/morning-cos/SKILL.md','.agents/skills/tasks/eod-review/SKILL.md','.agents/skills/tasks/system-maintenance/SKILL.md','.agents/skills/tasks/operator-executor/SKILL.md','.agents/skills/tasks/apple-reminders/SKILL.md','.agents/skills/knowledge/llm-wiki/SKILL.md']
def run(cmd,cwd,errors):
 p=subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 if p.returncode: errors.append(f"command failed: {' '.join(cmd)}\n{p.stdout}")
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--workspace',required=True); a=ap.parse_args(); ws=Path(a.workspace).expanduser().resolve(); errors=[]
 for rel in REQUIRED:
  if not (ws/rel).exists(): errors.append(f'missing required file: {rel}')
 links=ensure_no_symlinks(ws/'.agents')+ensure_no_symlinks(ws/'scripts')+ensure_no_symlinks(ws/'vault')
 errors += [f'symlink forbidden: {p}' for p in links]
 for base in [ws/'vault',ws/'.agents',ws/'scripts']:
  if base.exists():
   for p in base.rglob('*'):
    if p.is_file() and p.suffix in {'.md','.json','.jsonl','.yml','.yaml','.py'} and has_unresolved_placeholders(p.read_text(errors='ignore')): errors.append(f'unresolved placeholder in {p.relative_to(ws)}')
 for p in (ws/'vault/Operations/.machine').rglob('*.json'):
  try: json.loads(p.read_text() or '{}')
  except Exception as e: errors.append(f'invalid json {p.relative_to(ws)}: {e}')
 for p in (ws/'vault/Operations/.machine').rglob('*.jsonl'):
  for i,line in enumerate(p.read_text().splitlines(),1):
   if line.strip():
    try: json.loads(line)
    except Exception as e: errors.append(f'invalid jsonl {p.relative_to(ws)}:{i}: {e}')
 for skill in (ws/'.agents/skills').rglob('SKILL.md'):
  t=skill.read_text(errors='ignore'); fm=t.split('---',2)[1] if t.startswith('---') and len(t.split('---',2))>2 else ''
  if 'name:' not in fm or 'description:' not in fm: errors.append(f'invalid skill frontmatter: {skill.relative_to(ws)}')
 for cmd in [[sys.executable,'scripts/build-docs-index.py','--project-dir',str(ws)],[sys.executable,'scripts/lint-vault-links.py'],[sys.executable,'scripts/validate-operations-state.py'],[sys.executable,'scripts/render-backlog.py'],[sys.executable,'scripts/scheduler-dry-run.py'],[sys.executable,'scripts/privacy-scan.py','--mode','installed-workspace']]: run(cmd,ws,errors)
 if errors:
  print('\n'.join(errors)); print(f'{len(errors)} verification error(s)',file=sys.stderr); return 1
 print('workspace verification passed'); return 0
if __name__=='__main__': raise SystemExit(main())
