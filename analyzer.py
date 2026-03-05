from io import BytesIO
import streamlit as st
from google import genai

# Create Gemini client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def analyze_image(pil_image):
    # Convert PIL image to bytes
    buf = BytesIO()
    pil_image.save(buf, format="JPEG")
    image_bytes = buf.getvalue()

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=[
            {"type": "input_text", "text": "Analyze this image professionally."},
            {"type": "input_image", "image_bytes": image_bytes}
        ]
    )

    return response.text

