import uuid


def generate_account_number():
    return str(uuid.uuid4().hex[:16].upper())
