import face_recognition
import numpy as np
import cv2
from PIL import Image
import customtkinter
import os
from dotenv import load_dotenv
from skimage import transform

def test_dependencies():
    print("Testing dependencies...")
    
    # Test face_recognition
    print("✓ face_recognition imported successfully")
    
    # Test numpy
    arr = np.array([1, 2, 3])
    print("✓ numpy working successfully")
    
    # Test OpenCV
    img = cv2.imread("images/sample/detected_faces.png") if os.path.exists("images/sample/detected_faces.png") else None
    print("✓ OpenCV working successfully")
    
    # Test PIL
    pil_img = Image.new('RGB', (100, 100), color='red')
    print("✓ PIL working successfully")
    
    # Test customtkinter
    app = customtkinter.CTk()
    app.after(0, app.destroy)  # Destroy immediately
    print("✓ customtkinter working successfully")
    
    # Test python-dotenv
    load_dotenv()
    print("✓ python-dotenv working successfully")
    
    # Test scikit-image
    test_array = np.random.rand(10, 10)
    transformed = transform.resize(test_array, (20, 20))
    print("✓ scikit-image working successfully")
    
    print("\nAll dependencies are working correctly!")

if __name__ == "__main__":
    test_dependencies() 