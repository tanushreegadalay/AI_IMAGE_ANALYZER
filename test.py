from google import genai
from dotenv import load_dotenv
import os
from PIL import Image
from io import BytesIO
import base64

load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY environment variable not found!")
    print("Please set your API key in the .env file or environment variables.")
    exit(1)

# Initialize client only when API key is available
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    print(f"❌ Error initializing Gemini client: {e}")
    exit(1)

# Load image or create a test image if sample.jpg doesn't exist
if os.path.exists("sample.jpg"):
    image = Image.open("sample.jpg")
else:
    # Create a simple test image
    image = Image.new('RGB', (100, 100), color='red')
    print("Note: sample.jpg not found, using a generated test image.")

# Convert PIL image to base64
buf = BytesIO()
image.save(buf, format="JPEG")
buf.seek(0)
image_bytes = buf.getvalue()
image_base64 = base64.standard_b64encode(image_bytes).decode("utf-8")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        genai.types.Part(
            text="Describe this image in detail."
        ),
        genai.types.Part(
            inline_data=genai.types.Blob(
                mime_type="image/jpeg",
                data=image_base64
            )
        )
    ]
)

print("\n=== AI Image Analysis ===")
print(response.text)
print("=======================")