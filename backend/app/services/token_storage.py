import json
import os

TOKEN_FILE = "stored_tokens.json"


def save_tokens(access_token: str, refresh_token: str):
    with open(TOKEN_FILE, "w") as f:
        json.dump({
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, f)


def load_tokens():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        return json.load(f)