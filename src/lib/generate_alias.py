from coolname import generate_slug


def get_bank_alias(username: str) -> str:
    return f"{username}.{generate_slug(3).replace('-', '.')}"
