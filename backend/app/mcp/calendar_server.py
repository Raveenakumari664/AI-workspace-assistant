import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from mcp.server.fastmcp import FastMCP
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from app.services.token_storage import load_tokens
from app.core.config import settings

mcp = FastMCP("Calendar Server")


def get_calendar_service():
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
    service = build("calendar", "v3", credentials=creds)
    return service


@mcp.tool()
def list_todays_events() -> list:
    """Aaj ke saare Google Calendar events ki list deta hai"""
    from datetime import datetime, timezone

    service = get_calendar_service()

    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0).isoformat()
    end_of_day = now.replace(hour=23, minute=59, second=59).isoformat()

    events_result = service.events().list(
        calendarId="primary",
        timeMin=start_of_day,
        timeMax=end_of_day,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = events_result.get("items", [])
    event_summaries = []

    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        event_summaries.append({
            "id": event["id"],
            "summary": event.get("summary", "No Title"),
            "start": start,
        })

    return event_summaries


if __name__ == "__main__":
    mcp.run()