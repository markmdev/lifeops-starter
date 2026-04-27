from pathlib import Path
import shutil, subprocess, sys, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]
class TemplateRenderTest(unittest.TestCase):
 def test_defaults_use_lifeops_names(self):
  sys.path.insert(0,str(ROOT/'.agents/skills/setup-lifeops/scripts'))
  from common import default_answers
  ans=default_answers()
  self.assertTrue(ans['WORKSPACE_PATH'].endswith('/LifeOps'))
  self.assertEqual(ans['PRIVATE_REPO_NAME'],'lifeops-private')
  self.assertEqual(ans['PUBLIC_REPO_FULL_NAME'],'OWNER/lifeops-starter')

 def test_setup_skill_defines_required_heartbeats(self):
  text=(ROOT/'.agents/skills/setup-lifeops/SKILL.md').read_text()
  for marker in ['lifeops-scheduler','manual_pending_automation','lifeops-operator','lifeops-codex-session-harvester','lifeops-chronicle-harvester']:
   self.assertIn(marker,text)
  for marker in ['This is onboarding, not a silent installation task','Do not end after the workspace and scheduler are installed','starring the starter repo','Final Onboarding Handoff','Your LifeOps Workspace Is Live']:
   self.assertIn(marker,text)
  for marker in ['Do not present setup choices as YAML','Do not describe user-created worker threads as "blockers"','Do not create or update `TASKS_FOR_HUMAN.md`','does not ship a notifier skill']:
   self.assertIn(marker,text)

 def test_minimal_install_renders(self):
  target=Path(tempfile.mkdtemp(prefix='lifeops-test-')); shutil.rmtree(target)
  try:
   p=subprocess.run([sys.executable,'.agents/skills/setup-lifeops/scripts/install_workspace.py','--starter','.','--workspace',str(target),'--answers','tests/fixtures/answers.minimal.json'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
   self.assertEqual(p.returncode,0,p.stdout)
   self.assertTrue((target/'vault/Operations/ACTION_LEDGER.md').exists())
   cos=(target/'vault/Operations/Chief of Staff System.md').read_text()
   for marker in ['## Calendar Control','### Knowledge I/O','## Chronicle Harvester','## Codex Session Harvester','## Target Architecture']:
    self.assertIn(marker,cos)
   backlog=(target/'vault/Backlog.md').read_text()
   for marker in ['## How To Read This','## Active Backlog','## Today-Adjacent','## Waiting','## Candidates']:
    self.assertIn(marker,backlog)
   agents=(target/'AGENTS.md').read_text()
   for marker in ['continue the workflow until the task is fully completed','direct URL','Google Calendar directly']:
    self.assertIn(marker,agents)
   readme=(target/'README.private.md').read_text()
   for marker in ['## How This Works','vault/Notes and Journal.md','vault/Operations/','Optional systems']:
    self.assertIn(marker,readme)
   setup_report=(target/'.lifeops/setup-report.md').read_text()
   for marker in ['## Onboarding Decisions','Codex Session Harvester','Chronicle Harvester','Starter repo star','Slack']:
    self.assertIn(marker,setup_report)
   self.assertFalse((target/'vault/TASKS_FOR_HUMAN.md').exists())
   self.assertFalse((target/'.agents/skills/services/macos-notifier/SKILL.md').exists())
   for path in target.rglob('*'):
    if path.is_file() and path.suffix in {'.md','.json','.yml','.yaml','.py'}:
     self.assertNotIn('{{',path.read_text(errors='ignore'),str(path))
  finally: shutil.rmtree(target,ignore_errors=True)
if __name__=='__main__': unittest.main()
