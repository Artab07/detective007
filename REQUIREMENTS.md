Detective007 Forensic Sketch creation and Criminal Detection System
=====================================

This project is a forensic sketch creation and criminal detection system using Python, OpenCV, and the face_recognition library.

This package contains the models used by the face_recognition package.

Installation
------------

Before running the project, you need to install the required packages and libraries. Use the following commands:

1. Install OpenCV:

   .. code-block:: bash

      pip install opencv-python

2. Install NumPy:

   .. code-block:: bash

      pip install numpy

3. Install Pillow (PIL):

   .. code-block:: bash

      pip install pillow

4. Install face_recognition:

   .. code-block:: bash

      pip install face_recognition

5. Install customtkinter (for the frontend):

   .. code-block:: bash

      pip install customtkinter

6. Install dlib:

   - For Windows users with Python 3.12, you can use the provided wheel files:

     .. code-block:: bash

        pip install dlib-19.24.99-cp312-cp312-win_amd64.whl

   - For other systems or Python versions, you may need to install dlib from source or find an appropriate wheel file.

Running the Project
-------------------

1. To run the face detection script:

   .. code-block:: bash

      python main.py

2. To run the frontend:

   .. code-block:: bash

      python frontend.py

3. To test OpenCV-based face detection:

   .. code-block:: bash

      python test_opencv.py

4. To test the face_recognition library:

   .. code-block:: bash

      python test_recognition.py

Make sure you have the necessary image files in the `images/` directory and the required model files in the `models/` directory before running the scripts.

For more details about the project structure and requirements, please refer to the REQUIREMENTS.md file.

Model Information
-----------------

These models were created by `Davis King <https://github.com/davisking/dlib-models>`__ and are licensed in the public domain
or under CC0 1.0 Universal. See LICENSE for more information.

For more information about the face_recognition package, see `face_recognition <https://github.com/ageitgey/face_recognition>`__.

To run the project
-------------------
venv\Scripts\activate




def handle_upload():
        # Define allowed file types
        filetypes = (
            ('PNG files', '*.png'),
            ('JPEG files', '*.jpg;*.jpeg'),
            ('All files', '*.*')
        )
        
        # Open file dialog
        filename = filedialog.askopenfilename(
            title='Upload Sketch',
            initialdir='/',
            filetypes=filetypes
        )
        
        # Check if a file was selected
        if filename:
            # Get the file extension
            _, file_extension = os.path.splitext(filename)
            
            # Validate file type
            if file_extension.lower() in ['.png', '.jpg', '.jpeg']:
                # Here you can add code to handle the uploaded file
                print(f"File uploaded: {filename}")
                # You might want to:
                # 1. Copy the file to a specific directory
                # 2. Process the image
                # 3. Display the image
                # 4. Move to the next screen with the uploaded image
            else:
                # Show error message if invalid file type
                show_error_message("Invalid file type. Please select a PNG or JPG or JPEG file.")
    
    def show_error_message(message):
        error_label = ctk.CTkLabel(master=frame, 
                                 text=message, 
                                 text_color="red")
        error_label.pack(pady=12, padx=10)
        # Remove error message after 3 seconds
        frame.after(3000, error_label.destroy)
    