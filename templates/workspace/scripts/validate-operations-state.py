#!/usr/bin/env python3
import json
from pathlib import Path
OPS=Path('vault/Operations'); REQUIRED=['ACTION_LEDGER.md','DECISION_QUEUE.md','SIGNAL_INBOX.md','SCHEDULE.md','LOG.md','Chief of Staff System.md','Operator System.md','OPERATOR_QUEUE.md','OPERATOR_SCHEDULE.md','OPERATOR_LOG.md','OPERATOR_HANDOFF.md','EMAIL_DRAFT_QUEUE.md','EMAIL_LOG.md']
def main():
 errors=[]
 for n in REQUIRED:
  if not (OPS/n).exists(): errors.append(f'missing Operations/{n}')
 ledger=(OPS/'ACTION_LEDGER.md').read_text() if (OPS/'ACTION_LEDGER.md').exists() else ''
 for h in ['## Active','## Waiting','## Candidates','## Recently Done']:
  if h not in ledger: errors.append(f'ACTION_LEDGER missing {h}')
 sig=(OPS/'SIGNAL_INBOX.md').read_text() if (OPS/'SIGNAL_INBOX.md').exists() else ''
 for word in ['promoted','dismissed','superseded','needs_verification','ignored_noise']:
  if word not in sig: errors.append(f'SIGNAL_INBOX missing lifecycle word {word}')
 for p in (OPS/'.machine').rglob('*.json'):
  try: json.loads(p.read_text() or '{}')
  except Exception as e: errors.append(f'invalid json {p}: {e}')
 if errors: print('\n'.join(errors)); return 1
 print('operations state valid'); return 0
if __name__=='__main__': raise SystemExit(main())
