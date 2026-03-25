import sys
from dataclasses import dataclass
from typing import List

# ANSI Colors
C_RED = "\033[91m"
C_YELLOW = "\033[93m"
C_BLUE = "\033[94m"
C_GREEN = "\033[92m"
C_BOLD = "\033[1m"
C_RESET = "\033[0m"

def colorize(text: str, color: str, no_colors: bool = False) -> str:
    # Only colorize if output is a terminal and colors are not explicitly disabled
    if not no_colors and sys.stdout.isatty():
        return f"{color}{text}{C_RESET}"
    return text

@dataclass
class Finding:
    secret_type: str
    location: int
    risk: str
    content: str
    confidence: float = 0.0
    start: int = -1
    end: int = -1
    category: str = "generic"

    @property
    def redacted_value(self) -> str:
        c = self.content
        if len(c) > 12:
            return f"{c[:4]}...{c[-4:]}"
        elif len(c) > 4:
            return f"{c[0]}...{c[-1]}"
        else:
            return "****"

def format_report(findings: List[Finding], show_full: bool = False, show_short: bool = False, no_colors: bool = False) -> str:
    if not findings:
        return colorize("✅ No secrets detected.", C_GREEN, no_colors)

    # Sort and deduplicate findings
    unique = {}
    for f in findings:
        key = (f.location, f.content)
        if key not in unique or f.confidence > unique[key].confidence:
            unique[key] = f

    final = sorted(unique.values(), key=lambda x: (x.location, x.secret_type))

    # Summary Generation
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    severity_colors = {"HIGH": C_RED, "MEDIUM": C_YELLOW, "LOW": C_BLUE}

    header = colorize(f"⚠ Secrets detected: {len(final)}", C_BOLD, no_colors)
    summary_hdr = colorize("--- Summary ---", C_BOLD, no_colors)
    details_hdr = colorize("--- Details ---", C_BOLD, no_colors)

    if not (show_full or show_short):
        # Default mode: Only show severity counts
        severity_counts = {}
        for f in final:
            severity_counts[f.risk] = severity_counts.get(f.risk, 0) + 1

        report = f"{header}\n"
        report += f"{summary_hdr}\n"
        for risk in sorted(severity_counts.keys(), key=lambda x: severity_order.get(x, 99)):
            colored_risk = colorize(f"[{risk}]", severity_colors.get(risk, C_RESET), no_colors)
            report += f"{colored_risk}: {severity_counts[risk]}\n"
    else:
        # Detailed modes: Show breakdown by type and details
        summary_data = {} # (type, risk) -> count
        for f in final:
            k = (f.secret_type, f.risk)
            summary_data[k] = summary_data.get(k, 0) + 1

        sorted_summary = sorted(summary_data.items(), key=lambda x: (severity_order.get(x[0][1], 99), -x[1], x[0][0]))

        report = f"{header}\n"
        report += f"{summary_hdr}\n"
        for (stype, srisk), count in sorted_summary:
            colored_risk = colorize(f"[{srisk}]", severity_colors.get(srisk, C_RESET), no_colors)
            report += f"{colored_risk} {stype}: {count}\n"

        report += f"\n{details_hdr}\n"
        for f in final:
            colored_risk = colorize(f.risk, severity_colors.get(f.risk, C_RESET), no_colors)
            report += f"Type: {f.secret_type}\n"
            report += f"Location: line {f.location}\n"
            report += f"Risk: {colored_risk}\n"
            if show_full:
                report += f"Content: {f.content}\n\n"
            else:
                report += f"Content: {f.redacted_value} (redacted)\n\n"

    return report.strip()
