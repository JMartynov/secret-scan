import argparse
import sys
from detector import SecretDetector
from report import format_report

def main():
    parser = argparse.ArgumentParser(description="LLM Secrets Leak Detector CLI")
    parser.add_argument("input", nargs="?", help="File to scan or '-' for stdin")
    parser.add_argument("--text", help="Direct text to scan")
    parser.add_argument("--threshold", type=float, default=3.5, help="Entropy threshold (default 3.5)")
    parser.add_argument("--full", action="store_true", help="Show full content of secrets")
    parser.add_argument("--short", action="store_true", help="Show redacted content of secrets")
    parser.add_argument("--nocolors", action="store_true", help="Disable colored output")
    
    args = parser.parse_args()
    
    detector = SecretDetector(entropy_threshold=args.threshold)
    
    if args.text:
        content = args.text
    elif args.input == "-":
        content = sys.stdin.read()
    elif args.input:
        try:
            with open(args.input, "r") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # If no input is provided, show help
        parser.print_help()
        sys.exit(0)
    
    findings = detector.scan(content)
    print(format_report(findings, show_full=args.full, show_short=args.short, no_colors=args.nocolors))

if __name__ == "__main__":
    main()
