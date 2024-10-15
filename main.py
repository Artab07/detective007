import cv2
import numpy as np
from PIL import Image

def detect_faces(image_path):
    # Load the image using PIL
    pil_image = Image.open(image_path)

    # Convert image to RGB if it's not already
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')

    # Convert PIL image to numpy array
    image = np.array(pil_image)

    # Convert RGB to BGR (OpenCV uses BGR)
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Load the cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Convert into grayscale
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    return faces, image_bgr

def main():
    image_path = "images/myPhoto.png"  # Update this path to your image file
    faces, image = detect_faces(image_path)

    print(f"Number of faces detected: {len(faces)}")

    # Draw rectangle around the faces and save the output image
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)

    cv2.imwrite('detected_faces.png', image)
    print("Saved image with detected faces as 'detected_faces.png'")

    # Display face locations
    for i, (x, y, w, h) in enumerate(faces):
        print(f"Face {i+1} location - Top: {y}, Left: {x}, Bottom: {y+h}, Right: {x+w}")

if __name__ == "__main__":
    main()
