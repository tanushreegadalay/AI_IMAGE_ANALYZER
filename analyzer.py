import google.genai as genai

client = genai.Client(api_key="YOUR_API_KEY")

def analyze_image(image_path):
    # Read image as bytes
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",  # Stable model
        content=[
            {
                "type": "input_text",
                "text": "Analyze this image professionally."
            },
            {
                "type": "input_image",
                "image_bytes": image_bytes
            }
        ]
    )

    # Get the text result
    result_text = response.output_text
    return result_text

