from pathlib import Path
import subprocess, sys, unittest
ROOT=Path(__file__).resolve().parents[1]
class PrivacyTest(unittest.TestCase):
 def test_public_privacy_scan(self):
  p=subprocess.run([sys.executable,'.agents/skills/setup-lifeops/scripts/privacy_scan.py','--mode','public-repo','--root','.'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  self.assertEqual(p.returncode,0,p.stdout)
if __name__=='__main__': unittest.main()
