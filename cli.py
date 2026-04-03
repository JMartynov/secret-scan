import argparse
import sys
import os

from detector import SecretDetector
from obfuscator import Obfuscator
from report import format_report, format_sarif
from git_engine import GitEngine
from ignore_engine import IgnoreEngine
from cache_engine import load_cache, save_cache, is_commit_clean, mark_commit_clean
from concurrent.futures import ProcessPoolExecutor
import mmap

def scan_block_worker(block, data_dir, threshold, mode, force_scan_all, include_pii, pii_regions):
    # Re-initialize detector in each process to avoid serialization issues
    # and to ensure rules are loaded.
    detector = SecretDetector(entropy_threshold=threshold, data_dir=data_dir, mode=mode, force_scan_all=force_scan_all, include_pii=include_pii, pii_regions=pii_regions)
    findings = detector.scan(block.content)
    for f in findings:
        f.filepath = block.filepath
        f.location += block.start_line - 1
    return findings, block.commit_sha

class FileBlock:
    def __init__(self, filepath, content, start_line=1):
        self.filepath = filepath
        self.content = content
        self.start_line = start_line
        self.commit_sha = None

def scan_file_worker(filepath, data_dir, threshold, mode, force_scan_all, include_pii, pii_regions):
    try:
        detector = SecretDetector(entropy_threshold=threshold, data_dir=data_dir, mode=mode, force_scan_all=force_scan_all, include_pii=include_pii, pii_regions=pii_regions)
        all_findings = []
        file_size = os.path.getsize(filepath)
        if file_size > 10 * 1024 * 1024:
            # use mmap for large files > 10MB
            with open(filepath, 'rb') as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    chunk_size = 1024 * 1024 # 1MB
                    overlap = 8192 # 8KB overlap
                    pos = 0
                    line_offset = 1
                    while pos < file_size:
                        end = min(pos + chunk_size, file_size)
                        chunk_bytes = mm[pos:end]
                        try:
                            chunk = chunk_bytes.decode('utf-8', errors='replace')
                            findings = detector.scan(chunk)
                            for fn in findings:
                                fn.filepath = filepath
                                fn.location += line_offset - 1
                            all_findings.extend(findings)
                        except Exception:
                            pass

                        # Count lines in this chunk excluding the overlap part for the next iteration
                        actual_advance = chunk_size - overlap if end < file_size else end - pos
                        line_offset += chunk_bytes[:actual_advance].count(b'\n')
                        pos += actual_advance
        else:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                findings = detector.scan(f.read())
                for fn in findings:
                    fn.filepath = filepath
                all_findings.extend(findings)
        return all_findings
    except Exception:
        return []

def main():
    parser = argparse.ArgumentParser(description="LLM Secrets Leak Detector CLI")
    parser.add_argument("input", nargs="?", help="File to scan or '-' for stdin. Reads from stdin if omitted and piped.")
    parser.add_argument("--text", help="Direct text to scan")
    parser.add_argument("--threshold", type=float, default=3.5, help="Entropy threshold (default 3.5)")
    parser.add_argument("--full", action="store_true", help="Show full content of secrets")
    parser.add_argument("--short", action="store_true", help="Show redacted content of secrets")
    parser.add_argument("--nocolors", action="store_true", help="Disable colored output")
    parser.add_argument("--obfuscate", action="store_true", help="Obfuscate secrets in output")
    parser.add_argument("--obfuscate-mode", choices=["redact", "hash", "synthetic"], default="redact", help="Obfuscation mode")
    parser.add_argument("--force-scan-all", action="store_true", help="Force scan all lines, ignoring keyword search.")
    
    # Git Integration Flags
    parser.add_argument("--git-staged", action="store_true", help="Scan staged changes")
    parser.add_argument("--git-working", action="store_true", help="Scan working directory changes")
    parser.add_argument("--git-branch", help="Scan diff between branch and HEAD")
    parser.add_argument("--history", action="store_true", help="Scan git history")
    parser.add_argument("--since", help="Used with --history (e.g., '1 week ago')")
    parser.add_argument("--max-commits", type=int, help="Used with --history")
    
    # Advanced Flags
    parser.add_argument("--mode", choices=["fast", "balanced", "deep"], default="balanced", help="Scanning mode")
    parser.add_argument("--baseline", help="Baseline file to ignore existing secrets")
    parser.add_argument("--format", choices=["text", "sarif"], default="text", help="Output format")
    parser.add_argument("--fail-on-risk", choices=["CRITICAL", "HIGH", "MEDIUM", "LOW"], help="Fail if secrets with given risk or higher are found")
    parser.add_argument("--data-dir", default="data", help="Path to data directory for rules")
    parser.add_argument("--min-score", type=float, default=0.0, help="Minimum risk score to report (0-100)")

    # PII Flags
    parser.add_argument("--pii", action="store_true", help="Enable PII detection (emails, phones, etc.)")
    parser.add_argument("--pii-region", help="Comma-separated list of regions to limit PII scanning (e.g., US,UK)")

    args = parser.parse_args()

    ignore_engine = IgnoreEngine()
    if args.baseline:
        ignore_engine.load_baseline(args.baseline)

    pii_regions = args.pii_region.split(',') if args.pii_region else []

    detector = SecretDetector(entropy_threshold=args.threshold, data_dir=args.data_dir, ignore_engine=ignore_engine, mode=args.mode, force_scan_all=args.force_scan_all, include_pii=args.pii, pii_regions=pii_regions)
    git_engine = GitEngine()
    cache = load_cache()

    all_findings = []

    # Identify input source
    if args.git_staged or args.git_working or args.git_branch:
        blocks = []
        if args.git_staged:
            blocks = git_engine.get_staged_diff()
        elif args.git_working:
            blocks = git_engine.get_working_diff()
        elif args.git_branch:
            blocks = git_engine.get_branch_diff(args.git_branch)

        valid_blocks = [b for b in blocks if not ignore_engine.is_ignored_path(b.filepath)]
        if valid_blocks:
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(scan_block_worker, b, args.data_dir, args.threshold, args.mode, args.force_scan_all, args.pii, pii_regions) for b in valid_blocks]
                for future in futures:
                    findings, _ = future.result()
                    if findings:
                        all_findings.extend(findings)
    elif args.history:
        blocks = git_engine.get_history_diffs(since=args.since, max_commits=args.max_commits)
        
        # Filter blocks based on cache
        uncached_blocks = []
        for b in blocks:
            if b.commit_sha and is_commit_clean(b.commit_sha, cache):
                continue
            if ignore_engine.is_ignored_path(b.filepath):
                continue
            uncached_blocks.append(b)
        
        if uncached_blocks:
            # Parallel scan
            dirty_commits = set()
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(scan_block_worker, b, args.data_dir, args.threshold, args.mode, args.force_scan_all, args.pii, pii_regions) for b in uncached_blocks]
                for future in futures:
                    findings, sha = future.result()
                    if findings:
                        all_findings.extend(findings)
                        dirty_commits.add(sha)
            
            # Update cache: Mark commits that were scanned and had no findings as clean
            all_shas = {b.commit_sha for b in uncached_blocks if b.commit_sha}
            for sha in all_shas:
                if sha not in dirty_commits:
                    mark_commit_clean(sha, cache)
            save_cache(cache)
            
    elif args.obfuscate:
        # Specialized streaming obfuscation mode
        if args.text:
            from io import StringIO
            input_source = StringIO(args.text)
        elif args.input and args.input != '-':
            try:
                input_source = open(args.input, 'r', encoding='utf-8', errors='ignore')
            except Exception as e:
                print(f"Error opening file: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            input_source = sys.stdin

        obfuscator = Obfuscator(mode=args.obfuscate_mode)
        stream_iterator = detector.scan_stream(input_source, yield_non_matches=True)
        for line, findings in stream_iterator:
            sys.stdout.write(obfuscator.obfuscate(line, findings))
        
        if input_source is not sys.stdin:
            input_source.close()
        return
    else:
        # Standard scanning modes
        input_source = None
        if args.text:
            from io import StringIO
            input_source = StringIO(args.text)
        elif args.input and args.input != '-':
            if os.path.isdir(args.input):
                # Recursively scan directory
                filepaths = []
                for root, _, files in os.walk(args.input):
                    for file in files:
                        filepath = os.path.join(root, file)
                        rel_path = os.path.relpath(filepath, args.input)
                        if not ignore_engine.is_ignored_path(rel_path):
                            filepaths.append(filepath)
                if filepaths:
                    with ProcessPoolExecutor() as executor:
                        futures = [executor.submit(scan_file_worker, fp, args.data_dir, args.threshold, args.mode, args.force_scan_all, args.pii, pii_regions) for fp in filepaths]
                        for future in futures:
                            findings = future.result()
                            if findings:
                                all_findings.extend(findings)
            else:
                try:
                    all_findings.extend(scan_file_worker(args.input, args.data_dir, args.threshold, args.mode, args.force_scan_all, args.pii, pii_regions))
                except Exception as e:
                    print(f"Error opening file: {e}", file=sys.stderr)
                    sys.exit(1)
        elif not sys.stdin.isatty():
            input_source = sys.stdin
        
        if input_source:
            stream_iterator = detector.scan_stream(input_source)
            for _, findings in stream_iterator:
                all_findings.extend(findings)
            if input_source is not sys.stdin:
                input_source.close()
        elif not any([args.git_staged, args.git_working, args.git_branch, args.history, args.text, args.input]) and sys.stdin.isatty():
            # If no git flags, no input, and no pipe - show help
            parser.print_help()
            sys.exit(0)

    # Filter by minimum score
    if args.min_score > 0:
        all_findings = [f for f in all_findings if f.score >= args.min_score]

    # Output results
    if args.format == "sarif":
        print(format_sarif(all_findings))
    else:
        print(format_report(all_findings, show_full=args.full, show_short=args.short, no_colors=args.nocolors))

    # Exit code based on fail-on-risk
    if args.fail_on_risk:
        risk_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        fail_threshold = risk_levels.index(args.fail_on_risk)
        for f in all_findings:
            if risk_levels.index(f.risk) >= fail_threshold:
                sys.exit(1)

if __name__ == "__main__":
    main()
