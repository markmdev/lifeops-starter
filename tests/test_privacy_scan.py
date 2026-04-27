from pathlib import Path
import subprocess, sys, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]
class PrivacyScannerUnitTest(unittest.TestCase):
 def test_detects_secret(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp); (p/'bad.txt').write_text('sk-'+'a'*30)
   proc=subprocess.run([sys.executable,str(ROOT/'.agents/skills/setup-lifeops/scripts/privacy_scan.py'),'--mode','public-repo','--root',str(p)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
   self.assertNotEqual(proc.returncode,0,proc.stdout)
if __name__=='__main__': unittest.main()
