#!/usr/bin/env python3
from __future__ import annotations
import datetime as dt, getpass, json, re, shutil, subprocess
from pathlib import Path
PLACEHOLDER_RE=re.compile(r"{{([A-Z0-9_]+)}}")
TEXT_SUFFIXES={'.md','.txt','.json','.jsonl','.yml','.yaml','.py','.sh','.plist','.tmpl','.gitignore',''}
def repo_root(start:Path|None=None)->Path:
 cur=(start or Path.cwd()).resolve()
 for c in [cur,*cur.parents]:
  if (c/'templates').exists() and (c/'.agents').exists(): return c
 raise SystemExit('Could not locate starter repo root')
def load_json(path:Path)->dict:
 with path.open() as f: return json.load(f)
def write_json(path:Path,data:dict)->None:
 path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
def default_timezone()->str:
 try: return subprocess.check_output(['date','+%Z'],text=True).strip() or 'local'
 except Exception: return 'local'
def default_answers()->dict:
 os_user=getpass.getuser() or 'User'; display=os_user.replace('.',' ').replace('_',' ').title() or 'User'; today=dt.date.today().isoformat(); now=dt.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z'); workspace=str(Path('~/LifeOps').expanduser())
 return {'USER_NAME':display,'USER_SHORT_NAME':display.split()[0],'USER_EMAIL_OPTIONAL':'','COS_NAME':'Chief of Staff','OPERATOR_NAME':'Operator','TIMEZONE':default_timezone(),'WORKSPACE_PATH':workspace,'VAULT_PATH':str(Path(workspace)/'vault'),'PUBLIC_REPO_FULL_NAME':'OWNER/lifeops-starter','PRIVATE_REPO_NAME':'lifeops-private','INSTALL_DATE':today,'INSTALL_DATETIME_LOCAL':now,'TODAY_DISPLAY':today,'TODAY_YYYYMMDD':today.replace('-',''),'MORNING_BRIEF_TIME':'07:00','EOD_REVIEW_TIME':'22:00','SCHEDULER_CADENCE_MINUTES':'30','OPERATOR_CADENCE_MINUTES':'15','SCHEDULER_MODE':'manual_pending_automation','OBSIDIAN_ENABLED':'unknown','GMAIL_STATUS':'manual_unknown','CALENDAR_STATUS':'manual_unknown','CONTACTS_STATUS':'manual_unknown','MESSAGES_STATUS':'manual_unknown','CODEX_SESSIONS_STATUS':'manual_unknown','CHRONICLE_STATUS':'manual_unknown','GITHUB_STATUS':'manual_unknown','DRIVE_STATUS':'manual_unknown','REMINDERS_STATUS':'manual_unknown','BROWSER_STATUS':'manual_unknown','SLACK_STATUS':'manual_unknown','TONE_PREFERENCE':'concise, direct, warm, practical','OPERATOR_STATUS':'not_created','BACKUP_STATUS':'not_configured'}
def normalize_answers(raw:dict|None, workspace_override:str|None=None)->dict:
 ans=default_answers()
 if raw:
  for k,v in raw.items(): ans[k.upper()]='' if v is None else ('yes' if v is True else 'no' if v is False else str(v))
 ans['WORKSPACE_PATH']=str(Path(workspace_override or ans['WORKSPACE_PATH']).expanduser().resolve()); ans['VAULT_PATH']=str(Path(ans['WORKSPACE_PATH'])/'vault'); return derive_task_statuses(ans) if 'derive_task_statuses' in globals() else ans
def derive_task_statuses(ans:dict)->dict:
 ans['INBOX_ATTENTION_STATUS']='active' if ans.get('GMAIL_STATUS')=='available' else 'disabled'
 ans['MESSAGES_ATTENTION_STATUS']='active' if ans.get('MESSAGES_STATUS')=='available' else 'disabled'
 return ans
def merge_capability_statuses(ans:dict, cap:dict|None)->dict:
 if cap:
  m={'obsidian':'OBSIDIAN_ENABLED','gmail':'GMAIL_STATUS','calendar':'CALENDAR_STATUS','contacts':'CONTACTS_STATUS','messages':'MESSAGES_STATUS','codex_sessions':'CODEX_SESSIONS_STATUS','chronicle':'CHRONICLE_STATUS','github':'GITHUB_STATUS','drive':'DRIVE_STATUS','reminders':'REMINDERS_STATUS','browser':'BROWSER_STATUS','slack':'SLACK_STATUS'}
  for src,dst in m.items():
   status=cap.get('integrations',{}).get(src,{}).get('status')
   if status: ans[dst]=status
 return derive_task_statuses(ans)
def render_text(text:str,ctx:dict)->str:
 return PLACEHOLDER_RE.sub(lambda m:str(ctx.get(m.group(1),m.group(0))), text)
def has_unresolved_placeholders(text:str)->bool: return bool(PLACEHOLDER_RE.search(text))
def is_text_file(path:Path)->bool: return path.name=='.gitignore' or path.suffix in TEXT_SUFFIXES
def ensure_no_symlinks(path:Path)->list[Path]: return [] if not path.exists() else sorted(p for p in path.rglob('*') if p.is_symlink())
def is_relative_to(path:Path,parent:Path)->bool:
 try: path.resolve().relative_to(parent.resolve()); return True
 except ValueError: return False
def copy_render_tree(src:Path,dst:Path,ctx:dict)->None:
 for item in sorted(src.rglob('*')):
  rel=item.relative_to(src)
  if any(part in {'.DS_Store','__pycache__','__MACOSX'} for part in rel.parts) or item.is_dir(): continue
  if item.is_symlink(): raise RuntimeError(f'Template source is a symlink: {item}')
  out_rel=rel.with_suffix('') if rel.suffix=='.tmpl' else rel; out=dst/out_rel; out.parent.mkdir(parents=True,exist_ok=True)
  if is_text_file(item): out.write_text(render_text(item.read_text(errors='replace'),ctx))
  else: shutil.copy2(item,out)
  try: out.chmod(item.stat().st_mode)
  except OSError: pass
def redact_answers(ans:dict)->dict:
 secret=('TOKEN','SECRET','PASSWORD','KEY','COOKIE','OAUTH')
 return {k:('[redacted]' if any(s in k.upper() for s in secret) else v) for k,v in ans.items()}
