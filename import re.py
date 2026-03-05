import re
def validate_plate(text):
    # Magyar formátum: ABC-DEF-123
    if re.match(r'^[A-Z]{3}-[A-Z]{3}-\d{3}$', text):
        return text
    # Nemzetközi: ABC123 vagy ABC-123
    if re.match(r'^[A-Z]{3}-?\d{3,4}$', text):
        return text
    return None