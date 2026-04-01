import unittest
from git_engine import GitEngine

class TestGitEngine(unittest.TestCase):
    def test_parse_diff(self):
        diff = """diff --git a/file1.txt b/file1.txt
index e69de29..d95f3ad 100644
--- a/file1.txt
+++ b/file1.txt
@@ -1,3 +1,4 @@
 line1
-line2
+line2_mod
+line2_mod2
 line3
diff --git a/file2.txt b/file2.txt
--- a/file2.txt
+++ b/file2.txt
@@ -10,2 +10,3 @@
 ctx
+new_secret
"""
        engine = GitEngine()
        blocks = engine.parse_diff(diff)

        self.assertEqual(len(blocks), 2)

        self.assertEqual(blocks[0].filepath, 'file1.txt')
        self.assertEqual(blocks[0].content, 'line2_mod\nline2_mod2')
        self.assertEqual(blocks[0].start_line, 2)

        self.assertEqual(blocks[1].filepath, 'file2.txt')
        self.assertEqual(blocks[1].content, 'new_secret')
        self.assertEqual(blocks[1].start_line, 11)

    def test_parse_diff_multiline(self):
        diff = """diff --git a/multi.txt b/multi.txt
--- a/multi.txt
+++ b/multi.txt
@@ -1,5 +1,5 @@
 a
-b
+x
+y
+z
 c
"""
        engine = GitEngine()
        blocks = engine.parse_diff(diff)

        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].start_line, 2)
        self.assertEqual(blocks[0].content, 'x\ny\nz')

    def test_history_diffs(self):
        import subprocess
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize a new git repo in the temp directory
            subprocess.run(['git', 'init'], cwd=tmpdir, check=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=tmpdir, check=True)
            subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=tmpdir, check=True)

            # Create a file and commit it
            dummy_path = os.path.join(tmpdir, 'dummy.txt')
            with open(dummy_path, 'w') as f:
                f.write('dummy content\n')

            subprocess.run(['git', 'add', 'dummy.txt'], cwd=tmpdir, check=True)
            subprocess.run(['git', 'commit', '-m', 'Dummy commit'], cwd=tmpdir, check=True)

            # Switch to the temp directory to run the engine (which uses the current working directory)
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                engine = GitEngine()
                blocks = engine.get_history_diffs(max_commits=1)

                # Find the block for dummy.txt
                dummy_block = None
                for b in blocks:
                    if b.filepath == 'dummy.txt':
                        dummy_block = b
                        break

                self.assertIsNotNone(dummy_block)
                self.assertEqual(dummy_block.content, 'dummy content')
            finally:
                os.chdir(original_dir)

if __name__ == '__main__':
    unittest.main()
