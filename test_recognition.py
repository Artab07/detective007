import face_recognition
import numpy as np
from PIL import Image

# Load the image
image_path = r"images/myPhoto.png"
pil_image = Image.open(image_path)

print(f"Original image mode: {pil_image.mode}")
print(f"Original image size: {pil_image.size}")

# Convert image to RGB if it's not already
if pil_image.mode != 'RGB':
    pil_image = pil_image.convert('RGB')
    print("Converted image to RGB mode")

# Convert PIL image to numpy array
image = np.array(pil_image)

print(f"Numpy array shape: {image.shape}")
print(f"Numpy array dtype: {image.dtype}")

# Try different models
models = ['hog', 'cnn']

for model in models:
    try:
        print(f"\nTrying {model} model:")
        face_locations = face_recognition.face_locations(image, model=model)
        print(f"I found {len(face_locations)} face(s) in this photograph using the {model} model.")
        
        for face_location in face_locations:
            top, right, bottom, left = face_location
            print(f"A face is located at pixel location Top: {top}, Left: {left}, Bottom: {bottom}, Right: {right}")
    except Exception as e:
        print(f"An error occurred with {model} model: {str(e)}")

print("\nface_recognition version:", face_recognition.__version__)

# Save the processed image to verify it
Image.fromarray(image).save('processed_image.png')
print("Saved processed image as 'processed_image.png'")
