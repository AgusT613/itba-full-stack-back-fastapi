import os

# SQLITE
SQLITE_FILE_NAME = "database.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

# TABLE NAMES
BRANCH_OFFICES = "branch_offices"
USERS = "users"
BANK_ACCOUNTS = "bank_accounts"

# .ENV
ALGORITHM = "HS256"
SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# AUTH FASTAPI
TOKEN_URL = "/api/auth/token"

# ENDPOINTS
API_PREFIX = "/api"

AUTH_ROUTER_TAG = "auth"
AUTH_PREFIX = "/auth"
AUTH_GET_CURRENT_USER = "/users/me"
AUTH_GET_CURRENT_ACTIVE_USER = "/users/me/active"
AUTH_POST_TOKEN = "/token"
AUTH_POST_REGISTER = "/register"

ITBANK_ROUTER_TAG = "itbank"
ITBANK_PREFIX = "/itbank"
ITBANK_BRANCH_OFFICES = "/branch-offices"

HOME_BANKING_PREFIX = "/homebanking"

# EXCEPTION MESSAGES
INVALIDE_CREDENTIALS = "Could not validate credentials"
INACTIVE_USER = "Inactive user"
INCORRECT_USERNAME_OR_PASSWORD = "Incorrect username or password"
ALREADY_REGISTERED_USER = "Username already registered"
