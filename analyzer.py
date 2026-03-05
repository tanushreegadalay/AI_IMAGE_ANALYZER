from google import genai
import os

# DO NOT set api_version manually
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def analyze_image(image):
    response = client.models.generate_content(
    model="gemini-2.5-flash",  # ← use this
    messages=[
        {"role": "user", "content": ["Analyze this image professionally.", image]}
    ]
)
    return response.text