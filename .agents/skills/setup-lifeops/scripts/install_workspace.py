#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path
from common import copy_render_tree, default_answers, ensure_no_symlinks, is_relative_to, load_json, merge_capability_statuses, normalize_answers, redact_answers, repo_root, write_json
def run_optional(cmd,cwd):
 try: subprocess.run(cmd,cwd=cwd,check=True)
 except Exception as e: print(f'warning: optional command failed: {cmd}: {e}',file=sys.stderr)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--starter',default='.'); ap.add_argument('--workspace'); ap.add_argument('--answers'); ap.add_argument('--capabilities'); a=ap.parse_args()
 starter=Path(a.starter).expanduser().resolve(); starter=starter if (starter/'templates').exists() else repo_root(starter)
 raw=load_json(Path(a.answers)) if a.answers else {}; workspace=Path(a.workspace or raw.get('WORKSPACE_PATH') or default_answers()['WORKSPACE_PATH']).expanduser().resolve()
 if is_relative_to(workspace,starter): raise SystemExit(f'Refusing to install private workspace inside starter repo: {workspace}')
 links=ensure_no_symlinks(starter/'templates')+ensure_no_symlinks(starter/'.agents')
 if links: raise SystemExit('Template/source symlinks are forbidden:\n'+'\n'.join(map(str,links)))
 if workspace.exists() and any(workspace.iterdir()): raise SystemExit(f'Workspace path is not empty: {workspace}')
 caps=load_json(Path(a.capabilities)) if a.capabilities and Path(a.capabilities).exists() else None
 ans=merge_capability_statuses(normalize_answers(raw,str(workspace)),caps)
 workspace.mkdir(parents=True,exist_ok=True)
 copy_render_tree(starter/'templates/workspace',workspace,ans); copy_render_tree(starter/'templates/skills',workspace/'.agents/skills',ans)
 if (starter/'templates/obsidian').exists(): copy_render_tree(starter/'templates/obsidian',workspace/'vault',ans)
 write_json(workspace/'.lifeops/setup-answers.redacted.json',redact_answers(ans))
 if caps: write_json(workspace/'.lifeops/capabilities.json',caps)
 run_optional([sys.executable,'scripts/build-docs-index.py','--project-dir',str(workspace)],workspace); run_optional([sys.executable,'scripts/render-backlog.py'],workspace)
 print(f'LifeOps installed at: {workspace}'); print(f'Vault: {workspace/"vault"}'); print(f'Setup report: {workspace/".lifeops/setup-report.md"}'); return 0
if __name__=='__main__': raise SystemExit(main())
