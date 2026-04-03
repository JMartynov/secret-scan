import pytest
import os
import tempfile
import sys

from cli import scan_file_worker

def test_mmap_safety_large_file():
    # create a >10MB file with a secret across the chunk boundary
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as f:
        # newlines up to the chunk boundary to prevent matching generic AWS keys against the entire file line
        # chunk size is 1024*1024
        f.write('\n' * (1024 * 1024 - 10))
        # Secret exactly spanning the 1MB boundary (where 1MB chunk logic operates)
        # Note the logic operates per 1MB chunk
        f.write('AKIAIOSFODNN7EXAMPLE')
        f.write('\n' * (10 * 1024 * 1024))
        filepath = f.name

    try:
        findings = scan_file_worker(filepath, data_dir='data', threshold=3.5, mode='balanced', force_scan_all=False, include_pii=False, pii_regions=[])
        assert len(findings) > 0, "Should have found the AWS key despite mmap chunking"
    finally:
        os.remove(filepath)

if __name__ == "__main__":
    test_mmap_safety_large_file()
    print("test_mmap_safety_large_file passed.")
