import re

import exrex


def clean_regex_for_exrex(regex):
    clean = regex
    if clean.startswith('(?i)'):
        clean = clean[4:]
    clean = clean.replace('[\\n\\r]', '\n')
    # Replace \b with a space to satisfy word boundary in most cases
    clean = clean.replace('\\b', ' ')
    # Limit {X,Y} but NOT {X}
    clean = re.sub(r'\{(\d+),(\d+)\}', lambda m: f"{{{m.group(1)},{min(int(m.group(2)), 10)}}}", clean)
    return clean

regex = "(?i)(?:lexigram)(?:.|[\\n\\r]){0,40}\\b([a-zA-Z0-9\\S]{301})\\b"
clean = clean_regex_for_exrex(regex)
print(f"Cleaned: {clean}")
sample = exrex.getone(clean)
print(f"Sample: {sample}")
# Use standard re to check if it matches original regex
original_regex = "(?i)(?:lexigram)(?:.|[\\n\\r]){0,40}\\b([a-zA-Z0-9\\S]{301})\\b"
m = re.search(original_regex, sample)
print(f"Matches original: {m is not None}")
if m:
    print(f"Capture group 1: {m.group(1)}")
