import os
from io import BytesIO
from google import genai
import base64
import time
import hashlib
import json
from pathlib import Path
from google.genai.errors import ClientError

CACHE_FILE = Path("image_cache.json")

def get_cache():
    """Load cache from file"""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    """Save cache to file"""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except:
        pass

def get_image_hash(pil_image):
    """Generate hash of image for caching"""
    buf = BytesIO()
    pil_image.save(buf, format="JPEG")
    return hashlib.md5(buf.getvalue()).hexdigest()

def get_api_key():
    """Get API key from environment variables only"""
    # For security, we only use environment variables
    # Streamlit secrets should be set as environment variables in deployment
    return os.getenv("GEMINI_API_KEY")

def analyze_image(pil_image, max_retries=3):
    """Analyze image with quota management, error handling, and caching"""
    
    # Check cache first
    image_hash = get_image_hash(pil_image)
    cache = get_cache()
    if image_hash in cache:
        return f"✅ **Cached Result** (Saved API quota!)\n\n{cache[image_hash]}"

    # Get API key
    api_key = get_api_key()
    if not api_key:
        return "❌ **API Key Missing**\n\nNo API key found. Please:\n\n1. Set `GEMINI_API_KEY` environment variable\n2. For Render deployment, add it in your app settings under Environment\n3. Get a new key from [Google AI Studio](https://aistudio.google.com/)"

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
            # Cache the result
            cache[image_hash] = response.text
            save_cache(cache)
            return response.text

        except ClientError as e:
            if e.code == 429:  # Quota exceeded
                if attempt < max_retries - 1:
                    wait_time = min(30 * (2 ** attempt), 300)  # Exponential backoff, max 5 minutes
                    # Import streamlit only when needed for UI feedback
                    try:
                        import streamlit as st
                        st.warning(f"⚠️ API quota exceeded. Retrying in {wait_time} seconds... ({attempt + 1}/{max_retries})")
                    except:
                        pass  # If streamlit is not available, just wait
                    time.sleep(wait_time)
                    continue
                else:
                    return "❌ **API Quota Exceeded**\n\nYou've reached your free tier limit for today. Here are your options:\n\n🔄 **Wait**: Free tier resets daily at midnight UTC\n\n💳 **Upgrade**: Enable billing at [Google Cloud Console](https://console.cloud.google.com/billing)\n\n📊 **Check Usage**: Monitor at [Google AI Studio](https://aistudio.google.com/)\n\n⏰ **Retry Later**: The quota typically refreshes every 24 hours."
            elif e.code == 403:
                return "❌ **API Key Error**\n\nYour API key appears to be invalid, expired, or reported as leaked. Please:\n\n1. Get a **fresh API key** from [Google AI Studio](https://aistudio.google.com/)\n2. **Never commit API keys** to git or share them publicly\n3. Update your environment variables or redeploy\n4. Check that your Google Cloud project has billing enabled if needed"
