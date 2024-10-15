import cv2
import numpy as np
from PIL import Image

# Load the image using PIL
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

# Convert RGB to BGR (OpenCV uses BGR)
image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

# Load the cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Convert into grayscale
gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

# Detect faces
faces = face_cascade.detectMultiScale(gray, 1.1, 4)

# Print the number of faces detected
print(f"Number of faces detected: {len(faces)}")

# Draw rectangle around the faces and save the output image
for (x, y, w, h) in faces:
    cv2.rectangle(image_bgr, (x, y), (x+w, y+h), (255, 0, 0), 2)

cv2.imwrite('detected_faces.png', image_bgr)
print("Saved image with detected faces as 'detected_faces.png'")

# Display face locations
for i, (x, y, w, h) in enumerate(faces):
    print(f"Face {i+1} location - Top: {y}, Left: {x}, Bottom: {y+h}, Right: {x+w}")
