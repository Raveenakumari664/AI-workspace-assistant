from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_response(user_message: str) -> str:
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=user_message,
    )
    return response.text