"""
Problem: Validate an Email Address with Strict Rules
You need to check if an email like local@domain is valid based on these rules:
Rules for Local Part (before @):
Cannot have consecutive dots (..).
Cannot start or end with a dot (.).
Only letters, digits, and allowed symbols (like .) are okay.
Rules for Domain Part (after @):
Must be in the form: label.label... (at least two labels).
Each label:
Can contain letters, digits, and hyphens (-).
Cannot start or end with a hyphen.
Length: 1 to 63 characters.
The last label (TLD) must have at least 2 characters (e.g., .com).
No IP addresses like [192.168.0.1].
No spaces or quotes.
Edge Cases to Reject:
"a..b@example.com" → consecutive dots.
".abc@x.com" → starts with dot.
"abc.@x.com" → ends with dot.
"a@-ex.com" → domain starts with -.
"a@ex-.com" → domain ends with -.
"a@ex..com" → consecutive dots in domain.
"a@x.c" → TLD too short.
Valid Example:
✅ john.doe@example-domain.com
Invalid Examples:
❌ john..doe@example.com
❌ .john@example.com
"""

import re

def is_valid_email(email):
    # must contain exactly one @

    if email.count("@") != 1:
        return False

    local, domain = email.split("@")

    # Validation on LOCAL part
    # cannot be empty
    if not local:
        return False

    # cannot start or end with dot
    if local[0] == "." or local[-1] == ".":
        return False

    # cannot contain consecutive dots
    if ".." in local:
        return False

    # only letters, digits and dots allowed
    if not re.fullmatch(r"[A-Za-z0-9.]+", local):
        return False

    # DOMAIN specific validations
    # must contain one . atleast
    if "." not in domain:
        return False

    # cannot contain consecutive dots
    if ".." in domain:
        return False

    labels = domain.split(".")

    # labels rules
    for label in labels:
        # length 1 to 63
        if not (1 <= len(label) <= 63):
            return False

    return True



