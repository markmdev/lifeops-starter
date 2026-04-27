#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, platform, shutil, sqlite3, subprocess, tempfile
from pathlib import Path
from common import write_json
def command_status(cmd):
 path=shutil.which(cmd); return {'status':'available' if path else 'missing','detected_by':[f'command -v {cmd}'],'evidence':path or ''}
def run_status(args):
 try:
  p=subprocess.run(args,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=10); return p.returncode==0,p.stdout.strip()[:500]
 except Exception as e: return False,str(e)
def chronicle_status(home):
 detected=[]; evidence=[]
 persistent=home/'.codex/memories_extensions/chronicle/resources'
 legacy=[home/'.codex/chronicle',home/'.chronicle']
 tmp_candidates=[]
 for raw in [os.environ.get('TMPDIR'),tempfile.gettempdir()]:
  if raw:
   root=Path(raw)
   tmp_candidates += [root/'chronicle/screen_recording',root/'codex_chronicle',root/'chronicle']
 seen=set()
 for p in [persistent,*legacy,*tmp_candidates]:
  if str(p) in seen: continue
  seen.add(str(p))
  detected.append(str(p))
  try:
   if p.exists() and (p.is_file() or any(p.iterdir())):
    evidence.append(str(p))
  except Exception:
   pass
 ok,proc=run_status(['pgrep','-fl','codex_chronicle|chronicle'])
 detected.append('pgrep -fl codex_chronicle|chronicle')
 if ok and proc:
  evidence.append('running Chronicle-related process detected')
 status='available' if evidence else 'manual_unknown'
 return {'status':status,'detected_by':detected,'evidence':'; '.join(evidence[:4]),'why_it_matters':'Ambient work awareness.'}
def detect():
 system=platform.system(); home=Path.home(); core={'python':{'status':'available','detected_by':['running this script'],'evidence':platform.python_version()},'git':command_status('git'),'gh':command_status('gh'),'codex':command_status('codex')}
 if core['gh']['status']=='available':
  ok,e=run_status(['gh','auth','status'])
  core['gh_auth']={'status':'available' if ok else 'installed_not_authenticated','detected_by':['gh auth status'],'evidence':'gh auth status succeeded; account and token details not stored.' if ok else e}
 else: core['gh_auth']={'status':'missing','detected_by':['command -v gh'],'evidence':''}
 obs=Path('/Applications/Obsidian.app'); msg=home/'Library/Messages/chat.db'; sessions=home/'.codex/sessions'
 ms='unsupported_os'; me='not macOS'
 if system=='Darwin':
  if msg.exists():
   try: conn=sqlite3.connect(f'file:{msg}?mode=ro',uri=True); conn.execute('select count(*) from chat limit 1').fetchone(); conn.close(); ms='available'; me=str(msg)
   except Exception as e: ms='blocked_permission'; me=str(e)
  else: ms='missing'; me=str(msg)
 ints={'gmail':{'status':'manual_unknown','why_it_matters':'Inbox attention and email drafts.'},'calendar':{'status':'manual_unknown','why_it_matters':'Appointments and deadlines.'},'contacts':{'status':'manual_unknown','why_it_matters':'Person resolution.'},'messages':{'status':ms,'detected_by':[str(msg)],'evidence':me,'why_it_matters':'Message-derived tasks.'},'codex_sessions':{'status':'available' if sessions.exists() else 'missing','detected_by':[str(sessions)],'why_it_matters':'Cross-thread awareness.'},'chronicle':chronicle_status(home),'obsidian':{'status':'available' if obs.exists() else 'missing','detected_by':[str(obs)],'why_it_matters':'Human vault UI.'},'github':{'status':core['gh_auth']['status'],'detected_by':['gh auth status'],'why_it_matters':'Private backup.'},'browser':{'status':'manual_unknown','why_it_matters':'Assisted browser workflows.'},'drive':{'status':'manual_unknown','why_it_matters':'Document context.'},'reminders':{'status':'available' if system=='Darwin' else 'unsupported_os','why_it_matters':'Native reminders.'},'slack':{'status':'manual_unknown','why_it_matters':'Slack-derived work context and follow-up loops.'}}
 return {'core':core,'integrations':ints}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--json',dest='json_path'); a=ap.parse_args(); d=detect(); write_json(Path(a.json_path),d) if a.json_path else print(json.dumps(d,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
