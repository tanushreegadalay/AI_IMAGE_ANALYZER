"""Streamlit UI: thin client to the FastAPI analyzer backend."""

import os

import httpx
import streamlit as st
from PIL import Image

API_URL = os.getenv("API_URL", "http://localhost:8000")
ANALYZE_ENDPOINT = f"{API_URL}/api/analyze"
HEALTH_ENDPOINT = f"{API_URL}/api/health"

st.set_page_config(
    page_title="AI Image Analyzer",
    page_icon="🤖",
    layout="wide",
)

st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #4CAF50;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)


def _check_api_health() -> bool:
    """Return True if API is reachable."""
    try:
        r = httpx.get(HEALTH_ENDPOINT, timeout=2.0)
        return r.status_code == 200
    except Exception:
        return False


def _error_title(code: str) -> str:
    """Map error code to short UI title."""
    return {
        "QUOTA_EXCEEDED": "Quota exceeded",
        "API_KEY_INVALID": "Invalid API key",
        "API_KEY_MISSING": "API key missing",
        "ANALYSIS_FAILED": "Analysis failed",
    }.get(code, "Error")


st.sidebar.title("⚙ Settings")
st.sidebar.caption(f"Backend: {API_URL}")
if not _check_api_health():
    st.sidebar.error("Cannot reach analyzer service. Start the API with: uvicorn app.main:app --reload")
st.sidebar.markdown("Developed by Tanushree Gadalay")

st.title("🤖 AI-Powered Image Analyzer")
st.write("Upload an image and get AI-driven insights from the analyzer API.")

uploaded_file = st.file_uploader("📂 Upload an Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    col1, col2 = st.columns(2)

    with col1:
        st.image(image, caption="Uploaded Image")

    with col2:
        if st.button("🔍 Analyze Image"):
            if not _check_api_health():
                st.error("Cannot reach analyzer service. Ensure the API is running at " + API_URL)
            else:
                with st.spinner("Analyzing... Please wait..."):
                    try:
                        uploaded_file.seek(0)
                        file_bytes = uploaded_file.read()
                        files = {"file": (uploaded_file.name, file_bytes, uploaded_file.type or "image/jpeg")}
                        data = {}  # optional: add "model" form field here if needed
                        r = httpx.post(ANALYZE_ENDPOINT, files=files, data=data, timeout=60.0)
                        body = r.json()
                    except httpx.ConnectError:
                        st.error("Could not connect to the analyzer service. Is the API running?")
                    except Exception as e:
                        st.error(f"Request failed: {e}")
                    else:
                        if body.get("success") is True:
                            result = body.get("result", "")
                            cached = body.get("cached", False)
                            model = body.get("model", "")
                            st.success("✅ Analysis Complete!" + (" (cached)" if cached else ""))
                            if model:
                                st.caption(f"Model: {model}")
                            st.write(result)
                            st.download_button(
                                label="📥 Download Report",
                                data=result,
                                file_name="image_analysis.txt",
                                mime="text/plain",
                            )
                        else:
                            err = body.get("error", {})
                            code = err.get("code", "ANALYSIS_FAILED")
                            message = err.get("message", "Unknown error")
                            st.error(_error_title(code))
                            st.markdown(message)

st.markdown("---")
st.markdown("© 2026 AI Image Analyzer | Internship Project")
