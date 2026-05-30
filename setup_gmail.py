#!/usr/bin/env python3
"""
Setup Gmail OAuth token for Mhai2.
Reuses the existing Google OAuth client credentials from the Calendar token.
Run once: python3 setup_gmail.py
Token saved to: ~/.config/mhai/gmail_token.json
"""
import json
import webbrowser
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]

TOKEN_PATH = Path.home() / ".config" / "mhai" / "gmail_token.json"
CAL_TOKEN = Path.home() / ".config" / "gcalendar" / "default_v1.dat"

def main():
    # Extract client credentials from existing calendar token
    cal_data = json.load(open(CAL_TOKEN))
    client_config = {
        "installed": {
            "client_id": cal_data["client_id"],
            "client_secret": cal_data["client_secret"],
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": cal_data["token_uri"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)

    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes),
    }
    TOKEN_PATH.write_text(json.dumps(token_data, indent=2))
    print(f"✓ Gmail token saved to {TOKEN_PATH}")

if __name__ == "__main__":
    main()
