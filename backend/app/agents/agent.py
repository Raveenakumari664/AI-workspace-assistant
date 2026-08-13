import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from google import genai
from google.genai import types
from app.core.config import settings

from app.mcp.gmail_server import list_unread_emails
from app.mcp.calendar_server import list_todays_events
from app.mcp.drive_server import search_files

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Tools ki definition jo Gemini ko dikhengi
tools = [
    {
        "function_declarations": [
            {
                "name": "list_unread_emails",
                "description": "Gmail ke unread emails ki list deta hai, subject aur sender ke saath",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "max_results": {"type": "integer", "description": "Kitne emails chahiye"}
                    },
                },
            },
            {
                "name": "list_todays_events",
                "description": "Aaj ke Google Calendar events ki list deta hai",
                "parameters": {"type": "object", "properties": {}},
            },
            {
                "name": "search_files",
                "description": "Google Drive mein naam se files search karta hai",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search karne wala keyword"},
                        "max_results": {"type": "integer", "description": "Kitni files chahiye"},
                    },
                    "required": ["query"],
                },
            },
        ]
    }
]

# Tool naam ko actual Python function se map karte hain
available_functions = {
    "list_unread_emails": list_unread_emails,
    "list_todays_events": list_todays_events,
    "search_files": search_files,
}


def run_agent(user_message: str) -> str:
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=user_message,
        config=types.GenerateContentConfig(tools=tools),
    )

    candidate = response.candidates[0]
    part = candidate.content.parts[0]

    if part.function_call:
        function_name = part.function_call.name
        function_args = dict(part.function_call.args)

        function_to_call = available_functions[function_name]
        function_result = function_to_call(**function_args)

        follow_up = client.models.generate_content(
            model="gemini-flash-latest",
            contents=f"User asked: {user_message}\n\nTool result: {function_result}\n\nPlease summarize this nicely for the user.",
        )
        return follow_up.text

    return part.text