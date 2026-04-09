import subprocess
import os
import tempfile
import sys

repos = [
    "https://github.com/psf/requests.git",
    "https://github.com/pallets/flask.git",
    "https://github.com/pypa/pip.git",
    "https://github.com/django/django.git",
    "https://github.com/scrapy/scrapy.git",
    "https://github.com/boto/boto3.git",
    "https://github.com/urllib3/urllib3.git",
    "https://github.com/encode/httpx.git",
    "https://github.com/pydantic/pydantic.git",
    "https://github.com/pytest-dev/pytest.git",
    "https://github.com/celery/celery.git",
    "https://github.com/marshmallow-code/marshmallow.git",
    "https://github.com/tiangolo/fastapi.git",
    "https://github.com/certifi/python-certifi.git",
    "https://github.com/getsentry/sentry-python.git",
    "https://github.com/aws/aws-cli.git",
    "https://github.com/ansible/ansible.git",
    "https://github.com/pypa/virtualenv.git",
    "https://github.com/python-poetry/poetry.git",
    "https://github.com/sphinx-doc/sphinx.git"
]

results = {}

with tempfile.TemporaryDirectory() as tmpdir:
    for repo in repos:
        name = repo.split('/')[-1].replace('.git', '')
        print(f"Scanning {name}...")
        repo_path = os.path.join(tmpdir, name)
        # Shallow clone to save time
        subprocess.run(["git", "clone", "--depth", "50", repo, repo_path], capture_output=True)

        # We need to run the CLI on the downloaded repository directory
        # Let's write a small shell command to find all .py/.txt/.yml/.json files and scan them
        cmd = f"find {repo_path} -type f -not -path '*/.git/*' | xargs cat 2>/dev/null | {sys.executable} -m src.cli --mode fast"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        count = 0
        if "Secrets detected:" in res.stdout:
            import re
            m = re.search(r"Secrets detected:\s+(\d+)", res.stdout)
            if m:
                count = int(m.group(1))

        # Scan history as well to demonstrate history scanning orchestration
        cmd_history = f"cd {repo_path} && {sys.executable} -m src.cli --scan-history --limit-commits 10 --mode fast"
        res_hist = subprocess.run(cmd_history, shell=True, capture_output=True, text=True)
        hist_count = 0
        if "Secrets detected:" in res_hist.stdout:
            import re
            m = re.search(r"Secrets detected:\s+(\d+)", res_hist.stdout)
            if m:
                hist_count = int(m.group(1))

        results[name] = (count, hist_count)

print("\n--- Real World Scan Results ---")
for r, (c, hc) in results.items():
    print(f"{r}: {c} secrets detected in latest, {hc} in last 10 commits")
