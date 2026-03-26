import argparse
import sys
import os

from detector import SecretDetector
from obfuscator import Obfuscator
from report import format_report

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

    args = parser.parse_args()

    detector = SecretDetector(entropy_threshold=args.threshold)

    # Build a list of input sources: list of tuples (label, fileobj)
    input_sources = []

    if args.text:
        from io import StringIO
        input_sources.append(("<text>", StringIO(args.text)))
    elif args.input and args.input != '-':
        if os.path.isdir(args.input):
            # Walk the directory and open each regular file
            for root, dirs, files in os.walk(args.input):
                # skip some common unwanted dirs
                dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__'}]
                for fname in files:
                    path = os.path.join(root, fname)
                    try:
                        f = open(path, 'r', encoding='utf-8', errors='ignore')
                        input_sources.append((path, f))
                    except Exception as e:
                        print(f"Skipping {path}: {e}", file=sys.stderr)
        else:
            try:
                f = open(args.input, 'r', encoding='utf-8', errors='ignore')
                input_sources.append((args.input, f))
            except Exception as e:
                print(f"Error opening file: {e}", file=sys.stderr)
                sys.exit(1)
    elif args.input == '-' or not sys.stdin.isatty():
        input_sources.append(("<stdin>", sys.stdin))
    else:
        parser.print_help()
        sys.exit(0)

    try:
        if args.obfuscate:
            obfuscator = Obfuscator(mode=args.obfuscate_mode)
            for label, fobj in input_sources:
                stream_iterator = detector.scan_stream(fobj, force_scan_all=args.force_scan_all, yield_non_matches=True)
                for line, findings in stream_iterator:
                    sys.stdout.write(obfuscator.obfuscate(line, findings))
        else:
            all_findings = []
            for label, fobj in input_sources:
                stream_iterator = detector.scan_stream(fobj, force_scan_all=args.force_scan_all)
                for _, findings in stream_iterator:
                    all_findings.extend(findings)

            print(format_report(all_findings, show_full=args.full, show_short=args.short, no_colors=args.nocolors))
    finally:
        # Close any file objects we opened (don't close stdin)
        for label, fobj in input_sources:
            if fobj is not sys.stdin:
                try:
                    fobj.close()
                except Exception:
                    pass

if __name__ == "__main__":
    main()