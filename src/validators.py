def luhn_check(card_number: str) -> bool:
    """
    Validates a credit card number using the Luhn algorithm.
    Strips non-digit characters before validation.
    """
    digits = [int(c) for c in card_number if c.isdigit()]
    if not digits:
        return False

    checksum = 0
    reverse_digits = digits[::-1]

    for i, d in enumerate(reverse_digits):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d

    return checksum % 10 == 0

def validate_finding(finding_id: str, content: str) -> bool:
    """
    Dispatcher for specific finding validators based on rule ID.
    Returns True if the content passes validation or if no validator exists.
    Returns False if validation fails.
    """
    if finding_id == 'credit_card':
        return luhn_check(content)

    # By default, assume valid if no specific validator exists
    return True
