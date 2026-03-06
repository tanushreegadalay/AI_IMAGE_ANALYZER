from analyzer import analyze_image
from PIL import Image
import os

# Load image or create a test image if sample.jpg doesn't exist
if os.path.exists("sample.jpg"):
    image = Image.open("sample.jpg")
    print("Using sample.jpg for testing...")
else:
    # Create a simple test image
    image = Image.new('RGB', (100, 100), color='red')
    print("Note: sample.jpg not found, using a generated test image.")

# Test the analyzer function
print("Testing image analysis...")
result = analyze_image(image)
print("\nResult:")
print(result)