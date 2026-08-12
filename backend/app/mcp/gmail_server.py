import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from mcp.server.fastmcp import FastMCP
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from app.services.token_storage import load_tokens
from app.core.config import settings

mcp = FastMCP("Gmail Server")


def get_gmail_service():
    tokens = load_tokens()
    if not tokens:
        raise Exception("No saved tokens found. Please login first at /auth/login")

    creds = Credentials(
        token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
    )
    service = build("gmail", "v1", credentials=creds)
    return service


@mcp.tool()
def list_unread_emails(max_results: int = 5) -> list:
    """Unread Gmail emails ki list deta hai, subject aur sender ke saath"""
    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me", labelIds=["UNREAD"], maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    email_summaries = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me", id=msg["id"], format="metadata",
            metadataHeaders=["Subject", "From"]
        ).execute()

        headers = msg_data["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")

        email_summaries.append({
            "id": msg["id"],
            "subject": subject,
            "from": sender,
        })

    return email_summaries


if __name__ == "__main__":
    mcp.run()