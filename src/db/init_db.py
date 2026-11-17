"""Production Database Initializer.

Initializes production database tables, default branch offices, and an initial
system administrator account using environment variables. Idempotent and safe to run on startup.
"""

import os
from sqlmodel import Session, select
from src.db.connection import create_db_and_tables, engine
from src.models.accounts import BankAccount
from src.models.branch_offices import BranchOffice
from src.models.users import User
from src.utils.password import get_password_hash
from src.utils.text_generation import generate_account_number, get_bank_alias


def init_production_db(session: Session | None = None) -> None:
    """Initialize database tables and bootstrap an initial admin user for production."""
    create_db_and_tables()

    if session is None:
        with Session(engine) as sess:
            _execute_init(sess)
    else:
        _execute_init(session)


def _execute_init(session: Session) -> None:
    # 1. Initialize default branch office if none exist
    branch = session.exec(select(BranchOffice)).first()
    if not branch:
        branch = BranchOffice(
            name="ITBANK Central Office",
            address="Av. Eduardo Madero 399, CABA",
            contact="+54 11 55550100",
        )
        session.add(branch)
        session.flush()
        print("Default branch office created.")

    # 2. Check if an admin user already exists
    admin_user = session.exec(
        select(User).where(User.username == os.getenv("INITIAL_ADMIN_USERNAME", "admin"))
    ).first()

    if admin_user:
        print("Production database already initialized (admin user exists).")
        return

    # 3. Create initial admin user
    username = os.getenv("INITIAL_ADMIN_USERNAME", "admin")
    password = os.getenv("INITIAL_ADMIN_PASSWORD", "admin")
    email = os.getenv("INITIAL_ADMIN_EMAIL", "admin@itbank.com")
    full_name = os.getenv("INITIAL_ADMIN_FULL_NAME", "ITBANK Administrator")

    admin = User(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        disabled=False,
    )
    session.add(admin)
    session.flush()

    # 4. Provision initial primary bank account for admin
    account_number = generate_account_number()
    alias = get_bank_alias(username)
    account = BankAccount(
        user_id=admin.id,
        account_type="itbank",
        account_number=account_number,
        alias=alias,
        balance=0.0,
        description="Cuenta Corriente Administrador",
    )
    session.add(account)
    session.commit()
    print(f"Production initial admin user '{username}' and primary account successfully provisioned.")


if __name__ == "__main__":
    init_production_db()
