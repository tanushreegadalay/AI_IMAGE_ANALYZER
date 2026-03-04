import os
import google.generativeai as genai

# Configure Gemini API using Render environment variable
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_image(image):
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(
        ["Analyze this image professionally and describe it in detail.", image]
    )

    return response.text
