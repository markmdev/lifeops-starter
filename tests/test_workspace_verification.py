from pathlib import Path
import shutil, subprocess, sys, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]
class WorkspaceVerificationTest(unittest.TestCase):
 def test_verify_minimal_install(self):
  target=Path(tempfile.mkdtemp(prefix='lifeops-verify-')); shutil.rmtree(target)
  try:
   install=subprocess.run([sys.executable,'.agents/skills/setup-lifeops/scripts/install_workspace.py','--starter','.','--workspace',str(target),'--answers','tests/fixtures/answers.minimal.json'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
   self.assertEqual(install.returncode,0,install.stdout)
   verify=subprocess.run([sys.executable,'.agents/skills/setup-lifeops/scripts/verify_workspace.py','--workspace',str(target)],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
   self.assertEqual(verify.returncode,0,verify.stdout)
  finally: shutil.rmtree(target,ignore_errors=True)
if __name__=='__main__': unittest.main()
