import os
from io import BytesIO
import litellm
import base64
import time
import hashlib
import json
from pathlib import Path

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass

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

def _sanitize_env(value: str | None) -> str | None:
    """Trim surrounding quotes from dotenv values, if present."""
    if value and ((value.startswith('"') and value.endswith('"')) or
                  (value.startswith("'") and value.endswith("'"))):
        return value[1:-1]
    return value


def get_api_key(model):
    """Get API key from environment variables based on the model provider"""
    model_lower = model.lower()
    if model_lower.startswith("gpt") or model_lower.startswith("openai"):
        return _sanitize_env(os.getenv("OPENAI_API_KEY"))
    elif model_lower.startswith("gemini") or model_lower.startswith("google"):
        return _sanitize_env(os.getenv("GEMINI_API_KEY"))
    elif model_lower.startswith("claude") or model_lower.startswith("anthropic"):
        return _sanitize_env(os.getenv("ANTHROPIC_API_KEY"))
    else:
        # Default to GEMINI_API_KEY for backward compatibility
        return _sanitize_env(os.getenv("GEMINI_API_KEY"))

def get_model():
    """Get the AI model from environment variables"""
    return os.getenv("AI_MODEL", "gpt-4o")

def analyze_image(pil_image, max_retries=3):
    """Analyze image with quota management, error handling, and caching"""
    
    # Check cache first
    image_hash = get_image_hash(pil_image)
    cache = get_cache()
    if image_hash in cache:
        return f"✅ **Cached Result** (Saved API quota!)\n\n{cache[image_hash]}"

    # Get API key and model
    model = get_model()
    api_key = get_api_key(model)
    if not api_key:
        provider = model.split("/")[0] if "/" in model else model
        return f"❌ **API Key Missing**\n\nNo API key found for {provider}. Please set the appropriate environment variable:\n\n- For OpenAI models: `OPENAI_API_KEY`\n- For Gemini models: `GEMINI_API_KEY`\n- For Anthropic models: `ANTHROPIC_API_KEY`"

    # Set API key for the provider
    model_lower = model.lower()
    if model_lower.startswith("gpt") or model_lower.startswith("openai"):
        os.environ["OPENAI_API_KEY"] = api_key
    elif model_lower.startswith("gemini") or model_lower.startswith("google"):
        os.environ["GEMINI_API_KEY"] = api_key
    elif model_lower.startswith("claude") or model_lower.startswith("anthropic"):
        os.environ["ANTHROPIC_API_KEY"] = api_key
    # For other providers, assume the key is set appropriately

    # Convert PIL image to base64
    buf = BytesIO()
    pil_image.save(buf, format="JPEG")
    buf.seek(0)
    image_bytes = buf.getvalue()
    image_base64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this image professionally. Provide detailed insights about what you see."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]
        }
    ]

    for attempt in range(max_retries):
        try:
            response = litellm.completion(
                model=model,
                messages=messages
            )
            result = response.choices[0].message.content
            # Cache the result
            cache[image_hash] = result
            save_cache(cache)
            return result

        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "429" in error_str:
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
            elif "403" in error_str or "forbidden" in error_str or "invalid" in error_str:
                return "❌ **API Key Error**\n\nYour API key appears to be invalid, expired, or reported as leaked. Please:\n\n1. Get a **fresh API key** from [Google AI Studio](https://aistudio.google.com/)\n2. **Never commit API keys** to git or share them publicly\n3. Update your environment variables or redeploy\n4. Check that your Google Cloud project has billing enabled if needed"
            else:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Simple backoff
                    continue
                else:
                    return f"❌ **API Error**: {str(e)}"
