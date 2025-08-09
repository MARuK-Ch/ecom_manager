"""
Утилиты и регулярные выражения.
"""

import re

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
PHONE_REGEX = r"^\+?\d{10,15}$"
ADDRESS_REGEX = r".+"

def validate_email(email):
    return re.match(EMAIL_REGEX, email)

def validate_phone(phone):
    return re.match(PHONE_REGEX, phone)

def validate_address(address):
    return re.match(ADDRESS_REGEX, address)