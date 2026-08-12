import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from mcp.server.fastmcp import FastMCP
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from app.services.token_storage import load_tokens
from app.core.config import settings

mcp = FastMCP("Drive Server")


def get_drive_service():
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
    service = build("drive", "v3", credentials=creds)
    return service


@mcp.tool()
def search_files(query: str, max_results: int = 5) -> list:
    """Google Drive mein files search karta hai naam se"""
    service = get_drive_service()

    results = service.files().list(
        q=f"name contains '{query}'",
        pageSize=max_results,
        fields="files(id, name, mimeType, webViewLink)",
    ).execute()

    files = results.get("files", [])
    file_summaries = []

    for file in files:
        file_summaries.append({
            "id": file["id"],
            "name": file["name"],
            "type": file["mimeType"],
            "link": file.get("webViewLink", ""),
        })

    return file_summaries


if __name__ == "__main__":
    mcp.run()