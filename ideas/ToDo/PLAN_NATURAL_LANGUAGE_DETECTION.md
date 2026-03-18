# PLAN: Natural Language & Contextual Detection

## 1. Objective
Improve detection accuracy in LLM prompts by understanding the conversational context surrounding sensitive data.

## 2. Analogs & Research
- **Named Entity Recognition (NER)**: Using NLP models to identify "Secrets" as entities.
- **Spam Filtering**: Identifying patterns of "suspicious" conversation.

## 3. Implementation Details

### 3.1 Intent Markers
Expand the `contextual` category in rules to include "Intent Phrases":
- **English**: "my password is", "here are the credentials", "debug this log with the key"
- **French**: "mon mot de passe est"
- **Spanish**: "mi contraseña es"
- **German**: "mein passwort ist"

### 3.2 Proximity Logic
- Implement a "Context Window" of 100 characters around every high-entropy string.
- If a high-entropy string is found, scan the window for "Secret Indicators" (key, token, password, auth).
- Use a scoring multiplier: `Score *= 1.5` if an indicator is found within the window.

### 3.3 Prompt Leakage Patterns
Detect common "Prompt Injection" or "System Prompt" leakage attempts which often precede secret extraction:
- "Ignore all previous instructions"
- "System prompt:"
- "Translate the following secret"

## 4. Best Practices
- **Case Insensitivity**: Contextual markers must always be case-insensitive.
- **Fuzzy Matching**: Allow for minor typos in markers (e.g., "psswrd") using Levenshtein distance for higher-tier scoring.
- **Language Detection**: (Optional) Use a lightweight library like `langdetect` to swap context rule-sets dynamically.
