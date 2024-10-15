## Required Components:

1. Python environment (version not specified, but at least 3.5 based on setup.py)
2. OpenCV (cv2) library
3. NumPy library
4. Pillow (PIL) library
5. face_recognition library (version 1.2.3 or compatible)

## Core Files:

1. main.py: Contains the main face detection logic using OpenCV
2. test_opencv.py: Test script for OpenCV-based face detection
3. test_recognition.py: Test script for face_recognition library (currently having issues)

## Required Models:

1. models/shape_predictor_68_face_landmarks.dat

## Notes:

1. Ensure that all required libraries (OpenCV, NumPy, Pillow, face_recognition) are installed in your Python environment.
2. The face_recognition library is currently causing issues. Consider focusing on the OpenCV-based solution in main.py.
3. Keep the images/ directory (not shown in the structure but referenced in the code) for storing input images.
4. Retain the models/ directory with the required shape predictor file.

