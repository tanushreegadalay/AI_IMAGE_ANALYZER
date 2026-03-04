import os
from google import genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_image(image):
    model = genai.GenerativeModel("gemini-1.5-flash-latest")

    response = model.generate_content(
        ["Analyze this image professionally.", image]
    )

    return response.text