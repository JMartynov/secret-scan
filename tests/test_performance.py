import pytest
import subprocess
import os
import time
import shutil
from pathlib import Path

def create_perf_repo(repo_path, num_commits=100):
    repo_path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "user.email", "perf@example.com"], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "user.name", "Perf User"], cwd=repo_path, check=True)
    
    for i in range(num_commits):
        f = repo_path / f"file_{i}.txt"
        # Add some random data and a synthetic secret every 10 commits
        content = f"Some random data for commit {i}\n"
        if i % 10 == 0:
            content += f"AWS_KEY = 'AKIA{'X' * 16}'\n"
        f.write_text(content)
        subprocess.run(["git", "add", f"file_{i}.txt"], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", f"Commit {i}"], cwd=repo_path, check=True)

def test_history_scan_performance(tmp_path):
    repo_path = tmp_path / "perf_repo"
    create_perf_repo(repo_path, num_commits=50)
    
    project_root = os.getcwd()
    run_sh = os.path.join(project_root, "run.sh")
    
    # First run (no cache)
    start_time = time.time()
    result = subprocess.run(["secret-scan", "--history", "--mode", "deep", "--data-dir", os.path.join(project_root, "data")], cwd=repo_path, capture_output=True, text=True)
    first_run_duration = time.time() - start_time
    print(f"\nFirst run duration (50 commits): {first_run_duration:.2f}s")
    assert result.returncode == 0
    
    # Second run (with cache)
    start_time = time.time()
    result = subprocess.run(["secret-scan", "--history", "--mode", "deep", "--data-dir", os.path.join(project_root, "data")], cwd=repo_path, capture_output=True, text=True)
    second_run_duration = time.time() - start_time
    print(f"Second run duration (cached): {second_run_duration:.2f}s")
    
    # Cached run should be significantly faster
    assert second_run_duration < first_run_duration
    
    # Cleanup cache to not interfere with other tests if they share the environment
    cache_file = repo_path / ".secretscan_cache"
    if cache_file.exists():
        cache_file.unlink()

if __name__ == "__main__":
    # Manually run if needed
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        test_history_scan_performance(Path(tmp))
