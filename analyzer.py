import os
from io import BytesIO
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_image(pil_image):

    # Convert PIL image to bytes
    buf = BytesIO()
    pil_image.save(buf, format="JPEG")
    image_bytes = buf.getvalue()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            "Analyze this image professionally.",
            image_bytes
        ]
    )

    return response.text

