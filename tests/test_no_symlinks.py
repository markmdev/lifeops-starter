from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class NoSymlinksTest(unittest.TestCase):
 def test_no_symlinks(self):
  links=[p for p in ROOT.rglob('*') if '.git' not in p.parts and p.is_symlink()]
  self.assertEqual([],links)
if __name__=='__main__': unittest.main()
