import os
from io import BytesIO
from google import genai
import base64
import time
from google.genai.errors import ClientError

def get_api_key():
    """Get API key from Streamlit secrets or environment variables"""
    try:
        # Try Streamlit secrets first (for deployment)
        import streamlit as st
        return st.secrets["GEMINI_API_KEY"]
    except:
        # Fallback to environment variables (for local development)
        return os.getenv("GEMINI_API_KEY")

def analyze_image(pil_image, max_retries=3):
    """Analyze image with quota management and error handling"""

    # Get API key
    api_key = get_api_key()
    if not api_key:
        return "❌ **API Key Missing**\n\nNo API key found. Please:\n\n1. Set `GEMINI_API_KEY` environment variable\n2. Or add it to Streamlit secrets for deployment\n3. Get a new key from [Google AI Studio](https://aistudio.google.com/)"

    # Initialize client only when needed
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        return f"❌ **API Client Error**: {str(e)}"

    # Convert PIL image to bytes
    buf = BytesIO()
    pil_image.save(buf, format="JPEG")
    buf.seek(0)
    image_bytes = buf.getvalue()

    # Encode to base64
    image_base64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    for attempt in range(max_retries):
        try:
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

        except ClientError as e:
            if e.code == 429:  # Quota exceeded
                if attempt < max_retries - 1:
                    wait_time = min(30 * (2 ** attempt), 300)  # Exponential backoff, max 5 minutes
                    import streamlit as st
                    st.warning(f"⚠️ API quota exceeded. Retrying in {wait_time} seconds... ({attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    return "❌ **API Quota Exceeded**\n\nYou've reached your free tier limit for today. Here are your options:\n\n🔄 **Wait**: Free tier resets daily at midnight UTC\n\n💳 **Upgrade**: Enable billing at [Google Cloud Console](https://console.cloud.google.com/billing)\n\n📊 **Check Usage**: Monitor at [Google AI Studio](https://aistudio.google.com/)\n\n⏰ **Retry Later**: The quota typically refreshes every 24 hours."
            elif e.code == 403:
                return "❌ **API Key Error**\n\nYour API key appears to be invalid, expired, or reported as leaked. Please:\n\n1. Get a **fresh API key** from [Google AI Studio](https://aistudio.google.com/)\n2. **Never commit API keys** to git or share them publicly\n3. Update your environment variables or redeploy\n4. Check that your Google Cloud project has billing enabled if needed"
