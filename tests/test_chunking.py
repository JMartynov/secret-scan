import pytest
from src.cli import scan_file_worker
import os

def test_chunk_boundary_overlap():
    filepath = 'test_chunk_boundary.txt'
    with open(filepath, 'w') as f:
        # 1MB is 1,048,576 bytes
        f.write('\n' * (1024 * 1024 - 10))
        f.write('AKIAIOSFODNN7EXAMPLE')
        f.write('\n' * (10 * 1024 * 1024))

    findings = scan_file_worker(filepath, data_dir='data', threshold=3.5, mode='balanced', force_scan_all=False, include_pii=False, pii_regions=[])

    os.remove(filepath)
    assert len(findings) > 0, "Failed to match at chunk boundary!"

if __name__ == "__main__":
    test_chunk_boundary_overlap()
    print("Chunk boundary overlap works.")
