import json
import os

# We will populate it with the repos from scan_repos.py as a starting point
REPOS = [
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
    "https://github.com/sphinx-doc/sphinx.git",
    # Add dummy/test repos if we want to reach 500 later, for now this is the base list.
]

def main():
    target_path = os.path.join("data", "target_repos.json")
    # if it exists, maybe don't overwrite if not needed, but for curation script, we overwrite
    with open(target_path, "w") as f:
        json.dump(REPOS, f, indent=4)
    print(f"Curated {len(REPOS)} repositories and saved to {target_path}")

if __name__ == "__main__":
    main()
