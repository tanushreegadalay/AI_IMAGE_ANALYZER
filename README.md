# AI Image Analyzer 🤖

This is a simple AI-powered web app built using Streamlit.  
It allows users to upload an image and get AI-based analysis instantly.

I built this project as part of my internship / learning project to understand how AI APIs work with web applications.

---

## Features

- Upload JPG, JPEG, PNG images
- AI-based image analysis
- Clean dark UI
- Download analysis as text file
- Wide layout with sidebar

---

## Technologies Used

- Python
- Streamlit
- Pillow (PIL)
- Gemini 2.5 Flash API

---

## Project Structure

AI_IMAGE_ANALYZER/
│
├── app.py
├── analyzer.py
├── requirements.txt
└── README.md

---

## How to Run the Project

1. Clone the repository:

   git clone <your-repo-link>

2. Move into the folder:

   cd AI_IMAGE_ANALYZER

3. (Optional but recommended) Create virtual environment:

   python -m venv venv

4. Activate it:

   Windows:
   venv\Scripts\activate

   Mac/Linux:
   source venv/bin/activate

5. Install dependencies:

   pip install -r requirements.txt

6. Run the app:

   streamlit run app.py

The app will open in your browser at:

http://localhost:8501

---

## How It Works

- User uploads an image.
- The image is processed using Pillow.
- It is sent to the Gemini AI model through analyzer.py.
- The model returns analysis text.
- The result is displayed and can be downloaded.

---

## Future Improvements

- Add PDF report download
- Add model selection option
- Deploy on Streamlit Cloud
- Improve UI further

## Live Demo

The application is deployed and accessible at:

https://ai-image-analyzer-u0jp.onrender.com

---

## Author

Tanushree Gadalay  
Internship Project – 2026


