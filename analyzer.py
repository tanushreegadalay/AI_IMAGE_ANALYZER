import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_image(image):
    model = genai.GenerativeModel("gemini-1.0-pro-vision-latest")

    response = model.generate_content(
        ["Analyze this image professionally.", image]
    )

    return response.text