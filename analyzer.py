import os
from google import genai

client = genai.Client(api_key="AIzaSyCFO0CM8PvuQ9vuTY6M0u3whujYpkPMREY")

def analyze_image(image):
    response = client.models.generate_content(
        model="gemini-1.5-pro",   # ← changed here
        contents=[
            "Analyze this image professionally and describe it clearly.",
            image
        ]
    )

    return response.text