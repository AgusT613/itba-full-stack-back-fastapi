from datetime import datetime, timedelta
import random
from sqlmodel import Session, select
from src.db.connection import engine
from src.models.accounts import BankAccount
from src.models.branch_offices import BranchOffice
from src.models.cards import Card
from src.models.loans import Loan
from src.models.transfers import Transfer
from src.models.user_saved_aliases import UserSavedAlias
from src.models.users import User
from src.utils.password import get_password_hash
from src.utils.text_generation import fake


def seed_dev_database(session: Session | None = None) -> None:
    """Seed development database with admin, empty, and regular user accounts.

    Uses Faker to generate rich realistic data (addresses, phones, transactions, dates).
    Idempotent: skips if the admin user already exists.
    """
    if session is None:
        with Session(engine) as sess:
            _execute_seed(sess)
    else:
        _execute_seed(session)


def _execute_seed(session: Session) -> None:
    admin_existing = session.exec(
        select(User).where(User.username == "admin")
    ).first()
    if admin_existing:
        return

    # Seed branch offices using Faker
    branch1 = session.exec(
        select(BranchOffice).where(BranchOffice.name == "ITBANK Central")
    ).first()
    if not branch1:
        branch1 = BranchOffice(
            name="ITBANK Central",
            address=f"{fake.street_name()} {fake.building_number()}, CABA",
            contact=fake.phone_number()[:15],
        )
        session.add(branch1)
        session.flush()

    branch2 = session.exec(
        select(BranchOffice).where(BranchOffice.name == "ITBANK Norte")
    ).first()
    if not branch2:
        branch2 = BranchOffice(
            name="ITBANK Norte",
            address=f"{fake.street_name()} {fake.building_number()}, Buenos Aires",
            contact=fake.phone_number()[:15],
        )
        session.add(branch2)
        session.flush()

    # Passwords and PIN (credentials: admin/admin, user/user, empty/empty)
    admin_pw = get_password_hash("admin")
    user_pw = get_password_hash("user")
    empty_pw = get_password_hash("empty")
    pin_hash = get_password_hash("1234")

    # 1. Admin User (Rich profile with extensive data to showcase full UI)
    admin_full_name = f"{fake.first_name()} {fake.last_name()} (Admin)"
    admin_user = User(
        username="admin",
        email="admin@itbank.com",
        full_name=admin_full_name,
        hashed_password=admin_pw,
        disabled=False,
    )
    session.add(admin_user)
    session.flush()

    # Admin Accounts (Primary checking and secondary savings)
    admin_acc_primary = BankAccount(
        user_id=admin_user.id,
        account_type="itbank",
        account_number=fake.numerify(text="####################"),
        alias="admin.itbank.main",
        balance=2850000.50,
        description="Cuenta Corriente Principal ITBANK",
    )
    admin_acc_savings = BankAccount(
        user_id=admin_user.id,
        account_type="savings",
        account_number=fake.numerify(text="####################"),
        alias="admin.savings.vip",
        balance=920000.75,
        description="Caja de Ahorro Especial",
    )
    session.add(admin_acc_primary)
    session.add(admin_acc_savings)
    session.flush()

    # Admin Cards
    admin_holder = admin_full_name.upper()
    admin_cards = [
        Card(
            account_id=admin_acc_primary.id,
            user_id=admin_user.id,
            card_type="debit",
            last_four=fake.numerify(text="####"),
            card_holder_name=admin_holder,
            expiration_date=datetime.now() + timedelta(days=1200),
            brand="visa",
            status="active",
            hashed_pin=pin_hash,
            created_at=datetime.now() - timedelta(days=400),
            updated_at=datetime.now() - timedelta(days=400),
        ),
        Card(
            account_id=admin_acc_primary.id,
            user_id=admin_user.id,
            card_type="credit",
            last_four=fake.numerify(text="####"),
            card_holder_name=admin_holder,
            expiration_date=datetime.now() + timedelta(days=850),
            brand="mastercard",
            status="active",
            hashed_pin=pin_hash,
            created_at=datetime.now() - timedelta(days=300),
            updated_at=datetime.now() - timedelta(days=300),
        ),
        Card(
            account_id=admin_acc_primary.id,
            user_id=admin_user.id,
            card_type="credit",
            last_four=fake.numerify(text="####"),
            card_holder_name=admin_holder,
            expiration_date=datetime.now() + timedelta(days=1500),
            brand="amex",
            status="active",
            hashed_pin=pin_hash,
            created_at=datetime.now() - timedelta(days=200),
            updated_at=datetime.now() - timedelta(days=200),
        ),
        Card(
            account_id=admin_acc_savings.id,
            user_id=admin_user.id,
            card_type="credit",
            last_four=fake.numerify(text="####"),
            card_holder_name=admin_holder,
            expiration_date=datetime.now() - timedelta(days=30),  # expired/blocked
            brand="visa",
            status="blocked",
            hashed_pin=pin_hash,
            created_at=datetime.now() - timedelta(days=800),
            updated_at=datetime.now() - timedelta(days=30),
        ),
    ]
    for card in admin_cards:
        session.add(card)

    # Admin Loans
    admin_loans = [
        Loan(
            branch_office_id=branch1.id,
            user_id=admin_user.id,
            user_account_id=admin_user.id,
            loan_type="personal",
            start_date=datetime.now() - timedelta(days=180),
            due_date=15.0,
            amount=600000.0,
            status="active",
            interest_rate=0.32,
            total_repayment=792000.0,
            total_installments=12,
            remaining_installments=6,
        ),
        Loan(
            branch_office_id=branch2.id,
            user_id=admin_user.id,
            user_account_id=admin_user.id,
            loan_type="car",
            start_date=datetime.now() - timedelta(days=365),
            due_date=10.0,
            amount=1800000.0,
            status="active",
            interest_rate=0.25,
            total_repayment=2250000.0,
            total_installments=24,
            remaining_installments=12,
        ),
    ]
    for loan in admin_loans:
        session.add(loan)

    # Admin Saved Aliases (counterparties)
    session.add(UserSavedAlias(user_id=admin_user.id, alias="user.itbank.main"))
    session.add(UserSavedAlias(user_id=admin_user.id, alias=f"{fake.word()}.{fake.word()}.pay"))
    session.add(UserSavedAlias(user_id=admin_user.id, alias=f"{fake.word()}.services.ar"))

    # 2. Standard User (Receiver & counterpart in transfers)
    user_full_name = f"{fake.first_name()} {fake.last_name()}"
    standard_user = User(
        username="user",
        email="user@itbank.com",
        full_name=user_full_name,
        hashed_password=user_pw,
        disabled=False,
    )
    session.add(standard_user)
    session.flush()

    user_acc_primary = BankAccount(
        user_id=standard_user.id,
        account_type="itbank",
        account_number=fake.numerify(text="####################"),
        alias="user.itbank.main",
        balance=85400.0,
        description="Cuenta Sueldo ITBANK",
    )
    session.add(user_acc_primary)
    session.flush()

    # User Card
    user_card = Card(
        account_id=user_acc_primary.id,
        user_id=standard_user.id,
        card_type="debit",
        last_four=fake.numerify(text="####"),
        card_holder_name=user_full_name.upper(),
        expiration_date=datetime.now() + timedelta(days=900),
        brand="visa",
        status="active",
        hashed_pin=pin_hash,
        created_at=datetime.now() - timedelta(days=150),
        updated_at=datetime.now() - timedelta(days=150),
    )
    session.add(user_card)

    # User Saved Alias
    session.add(UserSavedAlias(user_id=standard_user.id, alias="admin.itbank.main"))

    # 3. Empty User (Zero state profile: signed up, no cards, no transfers, no loans)
    empty_user = User(
        username="empty",
        email="empty@itbank.com",
        full_name=f"{fake.first_name()} {fake.last_name()} (Nuevo)",
        hashed_password=empty_pw,
        disabled=False,
    )
    session.add(empty_user)
    session.flush()

    empty_acc = BankAccount(
        user_id=empty_user.id,
        account_type="itbank",
        account_number=fake.numerify(text="####################"),
        alias="empty.itbank.main",
        balance=0.0,
        description="Cuenta ITBANK",
    )
    session.add(empty_acc)

    # 4. Transfers between admin and standard user
    # Generate realistic historical transfer dates and amounts with Faker
    transfers = [
        Transfer(
            sender_id=admin_user.id,
            receiver_id=standard_user.id,
            balance=round(random.uniform(10000.0, 25000.0), 2),
            transfer_type="transfer",
            transfer_date=datetime.now() - timedelta(days=25, hours=3),
        ),
        Transfer(
            sender_id=admin_user.id,
            receiver_id=standard_user.id,
            balance=round(random.uniform(5000.0, 15000.0), 2),
            transfer_type="transfer",
            transfer_date=datetime.now() - timedelta(days=18, hours=5),
        ),
        Transfer(
            sender_id=admin_user.id,
            receiver_id=standard_user.id,
            balance=round(random.uniform(20000.0, 45000.0), 2),
            transfer_type="transfer",
            transfer_date=datetime.now() - timedelta(days=10, hours=2),
        ),
        Transfer(
            sender_id=standard_user.id,
            receiver_id=admin_user.id,
            balance=round(random.uniform(3000.0, 8000.0), 2),
            transfer_type="transfer",
            transfer_date=datetime.now() - timedelta(days=5, hours=6),
        ),
        Transfer(
            sender_id=admin_user.id,
            receiver_id=admin_user.id,
            balance=150000.0,
            transfer_type="deposit",
            transfer_date=datetime.now() - timedelta(days=2, hours=1),
        ),
    ]
    for transfer in transfers:
        session.add(transfer)

    session.commit()
    print("Database successfully seeded with 'admin', 'user', and 'empty' test accounts.")


if __name__ == "__main__":
    from src.db.connection import create_db_and_tables

    create_db_and_tables()
    seed_dev_database()
