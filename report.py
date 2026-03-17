from dataclasses import dataclass
from typing import List

@dataclass
class Finding:
    secret_type: str
    location: int
    risk: str
    content: str
    confidence: float = 0.0

    @property
    def redacted_value(self) -> str:
        c = self.content
        if len(c) > 12:
            return f"{c[:4]}...{c[-4:]}"
        elif len(c) > 4:
            return f"{c[0]}...{c[-1]}"
        else:
            return "****"

def format_report(findings: List[Finding], show_full: bool = False, show_short: bool = False) -> str:
    if not findings: return "✅ No secrets detected."
    
    # Sort and deduplicate findings
    # If multiple rules hit exactly same location/content, take highest confidence
    unique = {}
    for f in findings:
        key = (f.location, f.content)
        if key not in unique or f.confidence > unique[key].confidence:
            unique[key] = f
    
    final = sorted(unique.values(), key=lambda x: (x.location, x.secret_type))
    
    # Summary Generation
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    summary_data = {} # (type, risk) -> count
    for f in final:
        k = (f.secret_type, f.risk)
        summary_data[k] = summary_data.get(k, 0) + 1
        
    sorted_summary = sorted(summary_data.items(), key=lambda x: (severity_order.get(x[0][1], 99), -x[1], x[0][0]))

    report = f"⚠ Secrets detected: {len(final)}\n"
    report += "--- Summary ---\n"
    for (stype, srisk), count in sorted_summary:
        report += f"[{srisk}] {stype}: {count}\n"
    
    if show_full or show_short:
        report += "\n--- Details ---\n"
        for f in final:
            report += f"Type: {f.secret_type}\n"
            report += f"Location: line {f.location}\n"
            report += f"Risk: {f.risk}\n"
            if show_full:
                report += f"Content: {f.content}\n\n"
            else:
                report += f"Content: {f.redacted_value} (redacted)\n\n"
        
    return report.strip()
