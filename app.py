import streamlit as st
from PIL import Image
from analyzer import analyze_image

st.set_page_config(
    page_title="AI Image Analyzer",
    page_icon="🤖",
    layout="wide"
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

st.sidebar.title("⚙ Settings")
st.sidebar.info("AI Model: Gemini 2.5 Flash")
st.sidebar.markdown("Developed by Tanushree Gadalay")

st.title("🤖 AI-Powered Image Analyzer")
st.write("Upload an image and get AI-driven insights instantly.")

uploaded_file = st.file_uploader("📂 Upload an Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    col1, col2 = st.columns(2)

    with col1:
        st.image(image, caption="Uploaded Image", use_container_width=True)

    with col2:
        if st.button("🔍 Analyze Image"):
            with st.spinner("Analyzing... Please wait..."):
                result = analyze_image(image)
                st.success("✅ Analysis Complete!")
                st.write(result)
                st.download_button(
                    label="📥 Download Report",
                    data=result,
                    file_name="image_analysis.txt",
                    mime="text/plain"
                )

st.markdown("---")
st.markdown("© 2026 AI Image Analyzer | Internship Project")