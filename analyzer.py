from google import genai
from dotenv import load_dotenv
import os
import streamlit as st

api_key = st.secrets["GEMINI_API_KEY"]

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={"api_version": "v1beta"}
)

def analyze_image(image):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=["Analyze this image professionally.", image]
    )
    return response.text
