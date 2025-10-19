import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

ENV_FILE = ".env"
JWT_KEY_NAME = "JWT_SECRET_KEY"


# ----------------- Create .env if it doesn't exist -------------------------

if not os.path.exists(ENV_FILE):
    with open(ENV_FILE, "w") as f:
        f.write("# Environment variables for mental health backend\n")
        print(f"Created {ENV_FILE}.")


# --------------- Load current .env contents ------------------------
with open(ENV_FILE, "r") as f:
    env_lines = f.readlines()

# ------------------- Generate JWT secret key if missing ------------------------

jwt_exists = any(line.startswith(JWT_KEY_NAME) for line in env_lines)

if not jwt_exists:
    new_key = secrets.token_hex(32)  # 32-byte secure key
    with open(ENV_FILE, "a") as f:
        f.write(f"{JWT_KEY_NAME}={new_key}\n")
    print(f"Generated new JWT secret key and saved to {ENV_FILE}: {new_key}")
else:
    print(f"{JWT_KEY_NAME} already exists in {ENV_FILE}, no changes made.")