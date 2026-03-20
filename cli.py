import argparse
import sys
from detector import SecretDetector
from report import format_report
from obfuscator import Obfuscator

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
    
    input_source = None
    if args.text:
        from io import StringIO
        input_source = StringIO(args.text)
    elif args.input and args.input != '-':
        try:
            input_source = open(args.input, 'r', encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"Error opening file: {e}", file=sys.stderr)
            sys.exit(1)
    elif not sys.stdin.isatty():
        input_source = sys.stdin
    else:
        parser.print_help()
        sys.exit(0)

    if args.obfuscate:
        obfuscator = Obfuscator(mode=args.obfuscate_mode)
        stream_iterator = detector.scan_stream(input_source, force_scan_all=args.force_scan_all, yield_non_matches=True)
        for line, findings in stream_iterator:
            sys.stdout.write(obfuscator.obfuscate(line, findings))
    else:
        all_findings = []
        # The stream now yields (line, findings), so we adapt
        stream_iterator = detector.scan_stream(input_source, force_scan_all=args.force_scan_all)
        for _, findings in stream_iterator:
            all_findings.extend(findings)
        
        print(format_report(all_findings, show_full=args.full, show_short=args.short, no_colors=args.nocolors))

    if input_source and input_source is not sys.stdin:
        input_source.close()

if __name__ == "__main__":
    main()
