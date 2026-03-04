import os
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_image(image):
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[
            "Analyze this image professionally and describe it clearly.",
            image
        ]
    )

    return response.text