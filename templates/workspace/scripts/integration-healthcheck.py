#!/usr/bin/env python3
import argparse,json
from pathlib import Path
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--workspace',default='.'); a=ap.parse_args(); p=Path(a.workspace)/'.lifeops/capabilities.json'
 if not p.exists(): print('No capabilities.json found'); return 1
 data=json.loads(p.read_text()); print('# Integration Healthcheck')
 for k,v in sorted(data.get('integrations',{}).items()): print(f'- {k}: {v.get("status","unknown")}')
 return 0
if __name__=='__main__': raise SystemExit(main())
