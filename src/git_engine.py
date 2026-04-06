import subprocess
import re
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class DiffBlock:
    filepath: str
    start_line: int
    content: str
    commit_sha: str = ""

class GitEngine:
    def __init__(self):
        pass

    def _run_git(self, args: List[str]) -> str:
        try:
            result = subprocess.run(
                ["git"] + args,
                capture_output=True,
                text=False,
                check=True
            )
            return result.stdout.decode('utf-8', errors='replace')
        except subprocess.CalledProcessError:
            return ""

    def get_staged_files(self) -> List[Dict[str, str]]:
        output = self._run_git(["diff", "--staged", "--name-status"])
        files = []
        for line in output.splitlines():
            if not line:
                continue
            parts = line.split('\t')
            status = parts[0]
            if len(parts) >= 3 and status.startswith('R'):
                filepath = parts[2]
            elif len(parts) >= 2:
                filepath = parts[1]
            else:
                continue
            if not status.startswith('D'):  # Skip deleted files
                files.append({"filepath": filepath, "status": status})
        return files

    def get_diff(self, args: List[str]) -> List[DiffBlock]:
        output = self._run_git(args)
        return self.parse_diff(output)

    def get_staged_diff(self) -> List[DiffBlock]:
        return self.get_diff(["diff", "--staged", "--unified=3", "--text"])

    def get_working_diff(self) -> List[DiffBlock]:
        return self.get_diff(["diff", "--unified=3", "--text"])

    def get_branch_diff(self, branch: str) -> List[DiffBlock]:
        return self.get_diff(["diff", f"{branch}...HEAD", "--unified=3", "--text"])

    def get_history_diffs(self, since: str = None, max_commits: int = None) -> List[DiffBlock]:
        args = ["log", "-p", "--unified=3", "--text"]
        if since:
            args.extend(["--since", since])
        if max_commits:
            args.extend(["-n", str(max_commits)])
        return self.get_diff(args)

    def parse_diff(self, diff_text: str) -> List[DiffBlock]:
        blocks = []
        current_file = None
        current_block_lines = []
        current_start_line = 0
        current_line_offset = 0
        current_sha = ""

        for line in diff_text.splitlines():
            if line.startswith('commit '):
                current_sha = line.split(' ')[1]
            elif line.startswith('diff --git'):
                if current_file and current_block_lines:
                    blocks.append(DiffBlock(current_file, current_start_line + current_line_offset - len(current_block_lines), '\n'.join(current_block_lines), current_sha))
                    current_block_lines = []
                # Extract new filepath
                # diff --git a/file b/file
                match = re.match(r'^diff --git a/.*? b/(.*)$', line)
                if match:
                    current_file = match.group(1)
            elif line.startswith('@@'):
                if current_file and current_block_lines:
                    blocks.append(DiffBlock(current_file, current_start_line + current_line_offset - len(current_block_lines), '\n'.join(current_block_lines), current_sha))
                    current_block_lines = []

                # @@ -1,3 +1,4 @@
                match = re.search(r'\+([0-9]+)(?:,[0-9]+)? @@', line)
                if match:
                    current_start_line = int(match.group(1))
                    current_line_offset = 0
            elif line.startswith('+') and not line.startswith('+++'):
                if current_file:
                    current_block_lines.append(line[1:])
                    current_line_offset += 1
            elif line.startswith(' '):
                if current_block_lines:
                    blocks.append(DiffBlock(current_file, current_start_line + current_line_offset - len(current_block_lines), '\n'.join(current_block_lines), current_sha))
                    current_block_lines = []
                current_line_offset += 1
            elif line.startswith('-'):
                # - lines don't increment the + line offset
                pass
            elif line.startswith('\\'):
                # \ No newline at end of file
                pass

        if current_file and current_block_lines:
            blocks.append(DiffBlock(current_file, current_start_line + current_line_offset - len(current_block_lines), '\n'.join(current_block_lines), current_sha))

        return blocks
