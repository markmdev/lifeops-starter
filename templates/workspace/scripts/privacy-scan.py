#!/usr/bin/env python3
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
SECRET_PATTERNS=[re.compile(r'sk-[A-Za-z0-9_-]{20,}'),re.compile(r'ghp_[A-Za-z0-9_]{20,}'),re.compile(r'github_pat_[A-Za-z0-9_]{20,}'),re.compile(r'AIza[0-9A-Za-z_-]{20,}'),re.compile(r'-----BEGIN PRIVATE KEY-----'),re.compile(r'xox[baprs]-[A-Za-z0-9-]{10,}'),re.compile(r'ya29\.[A-Za-z0-9_-]{20,}'),re.compile(r'mail\.google\.com/mail/u/'),re.compile(r'x-apple-reminder://')]
ABS_PRIVATE_PATH=re.compile(r'/(Users|home)/(?!(\{\{|USER|user|example|runner|tmp)\b)[A-Za-z0-9._-]+/')
EMAIL_RE=re.compile(r'\b[A-Za-z0-9._%+-]+@(?:gmail\.com|icloud\.com|outlook\.com|yahoo\.com|proton\.me)\b')
PHONE_RE=re.compile(r'(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?!\d)')
SKIP={'.git','.venv','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache'}; FORBIDDEN={'.DS_Store','__MACOSX'}
SKIP_FILES={
 '.agents/skills/setup-lifeops/scripts/privacy_scan.py',
 'templates/workspace/scripts/privacy-scan.py',
 'scripts/privacy-scan.py',
}
def files(root):
 for p in root.rglob('*'):
  if any(part in SKIP for part in p.parts): continue
  if p.is_file(): yield p
def scan(path,root,mode):
 rel=path.relative_to(root); f=[]
 if rel.as_posix() in SKIP_FILES:
  return f
 if path.name in FORBIDDEN or path.suffix=='.pyc': f.append(f'{rel}: forbidden generated file')
 if path.is_symlink(): f.append(f'{rel}: symlink forbidden')
 if mode=='public-repo' and path.name.startswith('.env'): f.append(f'{rel}: env files are forbidden')
 try: text=path.read_text(errors='ignore')
 except Exception: return f
 for pat in SECRET_PATTERNS:
  if pat.search(text): f.append(f'{rel}: secret-like pattern {pat.pattern}')
 if mode=='public-repo':
  if ABS_PRIVATE_PATH.search(text): f.append(f'{rel}: private absolute path')
  for email in EMAIL_RE.findall(text):
   if email!='user@example.com': f.append(f'{rel}: real-looking personal email {email}')
  if PHONE_RE.search(text): f.append(f'{rel}: real-looking phone number')
 return f
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--mode',choices=['public-repo','installed-workspace'],required=True); ap.add_argument('--root',default='.'); a=ap.parse_args(); root=Path(a.root).resolve(); findings=[]
 for p in files(root): findings.extend(scan(p,root,a.mode))
 if findings:
  print('\n'.join(findings)); print(f'{len(findings)} finding(s)',file=sys.stderr); return 1
 print('privacy scan passed'); return 0
if __name__=='__main__': raise SystemExit(main())
