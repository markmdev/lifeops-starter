#!/usr/bin/env python3
from pathlib import Path
S=Path('vault/Operations/SCHEDULE.md')
def main():
 text=S.read_text() if S.exists() else ''; active=[]; cur=None
 for line in text.splitlines():
  if line.startswith('### '): cur=line[4:].strip()
  elif cur and line.strip().lower() in {'status: active','- status: active'}: active.append(cur)
 print('Scheduler dry run')
 for t in active or ['no active tasks']: print(f'- {t}')
 return 0
if __name__=='__main__': raise SystemExit(main())
