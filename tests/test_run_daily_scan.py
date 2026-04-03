import pytest
import os
import tempfile
import json
from unittest.mock import patch

from tools.run_daily_scan import load_json, save_json, generate_report

def test_load_save_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test.json")
        assert load_json(filepath, {"default": True}) == {"default": True}

        save_json(filepath, {"saved": True})
        assert load_json(filepath, {}) == {"saved": True}

def test_generate_report():
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch('tools.run_daily_scan.REPORTS_DIR', tmpdir):
            results = {
                "https://github.com/test/repo.git": [
                    {"rule_id": "test_rule", "source": "test.py", "line_number": 1, "value": "***", "severity": "HIGH"}
                ]
            }
            generate_report(results)

            # Check if a report was created
            files = os.listdir(tmpdir)
            assert len(files) == 1
            assert files[0].startswith("report_")
            assert files[0].endswith(".md")

            with open(os.path.join(tmpdir, files[0]), "r") as f:
                content = f.read()
                assert "test_rule" in content
                assert "***" in content
                assert "https://github.com/test/repo.git" in content
