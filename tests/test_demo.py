import subprocess
import os

def test_demo_execution():
    # Run demo.sh and capture output
    # Ensure run.sh is executable
    os.chmod("run.sh", 0o755)
    os.chmod("demo.sh", 0o755)
    
    # Increase timeout because the 1MB file benchmark in the demo may take longer
    # due to strict regex evaluations and concurrency spinup on some environments.
    result = subprocess.run(["./demo.sh"], capture_output=True, text=True, timeout=600)
    print("DEBUG: Full stdout from demo.sh:")
    print(result.stdout)
    print("DEBUG: Full stderr from demo.sh:")
    print(result.stderr)

    # Check if execution was successful
    assert result.returncode == 0
    
    # Check for key sections in the output
    assert "Initializing Advanced Demo Environment" in result.stdout
    assert "Part 1: Default Output (Summary Only)" in result.stdout
    assert "Part 2: Short Output (Summary + Redacted Details)" in result.stdout
    assert "Part 3: Full Output (Summary + Full Details)" in result.stdout
    assert "Part 4: No Colors Output" in result.stdout
    assert "Part 5: Streaming Output (Piping without -)" in result.stdout
    assert "Part 6: 1MB Performance Benchmark (Summary)" in result.stdout
    assert "Demo Complete" in result.stdout
    
    # Check if redacted content is present in Part 2
    # We look for AKIA...CDEF string which should be there for AWS key redaction
    assert "AKIA...CDEF" in result.stdout
    
    # Ensure no ANSI color codes in Part 4 output
    # This is tricky because Part 4 is just a section of the whole output.
    # But we can check if the output *after* "Part 4" and *before* "Part 5" contains color codes.
    part4_start = result.stdout.find("--- Part 4: No Colors Output ---")
    part5_start = result.stdout.find("--- Part 5: Streaming Output (Piping without -) ---")
    part4_output = result.stdout[part4_start:part5_start]
    assert "\033[" not in part4_output
