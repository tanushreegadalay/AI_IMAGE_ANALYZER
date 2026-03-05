import os
from io import BytesIO
from google import genai
import base64

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_image(pil_image):

    # Convert PIL image to bytes
    buf = BytesIO()
    pil_image.save(buf, format="JPEG")
    buf.seek(0)
    image_bytes = buf.getvalue()
    
    # Encode to base64
    image_base64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            genai.types.Part(
                text="Analyze this image professionally. Provide detailed insights about what you see."
            ),
            genai.types.Part(
                inline_data=genai.types.Blob(
                    mime_type="image/jpeg",
                    data=image_base64
                )
            )
        ]
    )

    return response.text

