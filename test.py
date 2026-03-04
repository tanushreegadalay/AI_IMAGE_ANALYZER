from google import genai
from dotenv import load_dotenv
import os
from PIL import Image

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={"api_version": "v1beta"}
)

# Load image
image = Image.open("sample.jpg")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        "Describe this image in detail.",
        image
    ]
)

print(response.text)