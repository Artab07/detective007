import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from supabase_config import add_criminal_record
import face_recognition
import numpy as np
import os
from PIL import Image
import logging
import base64
from supabase import create_client
from dotenv import load_dotenv
from face_matcher import FaceMatcher
import multiprocessing

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def encode_images_worker(image_paths, queue):
    import face_recognition
    import numpy as np
    import cv2
    import os
    results = []
    for path in image_paths:
        try:
            image = face_recognition.load_image_file(path)
            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                results.append((True, encodings[0], path))
            else:
                results.append((False, f'No face detected in {os.path.basename(path)}', path))
        except Exception as e:
            results.append((False, str(e), path))
    queue.put(results)

class AddCriminalWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Warm up dlib/face_recognition on main thread to prevent freezing in threads
        import numpy as np
        import face_recognition
        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
        try:
            _ = face_recognition.face_encodings(dummy_img)
        except Exception:
            pass

        # Configure window
        self.title("Add Criminal Record")
        self.geometry("800x600")
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.scrollable_frame.pack(fill="both", expand=True)
        
        # Create form fields
        self.create_form_fields()
        
        # Create buttons
        self.create_buttons()
        
        # Create progress overlay
        self.create_progress_overlay()
        
        # Store image paths
        self.face_image_path = None
        self.additional_images = []
        
    def create_form_fields(self):
        # Personal Information
        personal_frame = ctk.CTkFrame(self.scrollable_frame)
        personal_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(personal_frame, text="Personal Information", font=("Roboto", 16, "bold")).pack(pady=5)
        
        # Name
        ctk.CTkLabel(personal_frame, text="Full Name:").pack(anchor="w", padx=10)
        self.name_entry = ctk.CTkEntry(personal_frame)
        self.name_entry.pack(fill="x", padx=10, pady=5)
        
        # Date of Birth
        ctk.CTkLabel(personal_frame, text="Date of Birth (YYYY-MM-DD):").pack(anchor="w", padx=10)
        self.dob_entry = ctk.CTkEntry(personal_frame)
        self.dob_entry.pack(fill="x", padx=10, pady=5)
        
        # Physical Description
        physical_frame = ctk.CTkFrame(self.scrollable_frame)
        physical_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(physical_frame, text="Physical Description", font=("Roboto", 16, "bold")).pack(pady=5)
        
        # Height
        ctk.CTkLabel(physical_frame, text="Height (cm):").pack(anchor="w", padx=10)
        self.height_entry = ctk.CTkEntry(physical_frame)
        self.height_entry.pack(fill="x", padx=10, pady=5)
        
        # Weight
        ctk.CTkLabel(physical_frame, text="Weight (kg):").pack(anchor="w", padx=10)
        self.weight_entry = ctk.CTkEntry(physical_frame)
        self.weight_entry.pack(fill="x", padx=10, pady=5)
        
        # Eye Color
        ctk.CTkLabel(physical_frame, text="Eye Color:").pack(anchor="w", padx=10)
        self.eye_color_entry = ctk.CTkEntry(physical_frame)
        self.eye_color_entry.pack(fill="x", padx=10, pady=5)
        
        # Hair Color
        ctk.CTkLabel(physical_frame, text="Hair Color:").pack(anchor="w", padx=10)
        self.hair_color_entry = ctk.CTkEntry(physical_frame)
        self.hair_color_entry.pack(fill="x", padx=10, pady=5)
        
        # Criminal Information
        criminal_frame = ctk.CTkFrame(self.scrollable_frame)
        criminal_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(criminal_frame, text="Criminal Information", font=("Roboto", 16, "bold")).pack(pady=5)
        
        # Crimes
        ctk.CTkLabel(criminal_frame, text="Crimes (comma separated):").pack(anchor="w", padx=10)
        self.crimes_entry = ctk.CTkEntry(criminal_frame)
        self.crimes_entry.pack(fill="x", padx=10, pady=5)
        
        # Status
        ctk.CTkLabel(criminal_frame, text="Status:").pack(anchor="w", padx=10)
        self.status_entry = ctk.CTkEntry(criminal_frame)
        self.status_entry.pack(fill="x", padx=10, pady=5)
        
        # Last Known Location
        ctk.CTkLabel(criminal_frame, text="Last Known Location:").pack(anchor="w", padx=10)
        self.location_entry = ctk.CTkEntry(criminal_frame)
        self.location_entry.pack(fill="x", padx=10, pady=5)
        
        # Notes
        ctk.CTkLabel(criminal_frame, text="Additional Notes:").pack(anchor="w", padx=10)
        self.notes_entry = ctk.CTkTextbox(criminal_frame, height=100)
        self.notes_entry.pack(fill="x", padx=10, pady=5)
        
    def create_buttons(self):
        button_frame = ctk.CTkFrame(self.scrollable_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # Upload Face Image button
        self.face_image_btn = ctk.CTkButton(
            button_frame,
            text="Upload Face Image",
            command=self.upload_face_image
        )
        self.face_image_btn.pack(side="left", padx=5, pady=5)
        
        # Upload Additional Images button
        self.additional_images_btn = ctk.CTkButton(
            button_frame,
            text="Upload Additional Images",
            command=self.upload_additional_images
        )
        self.additional_images_btn.pack(side="left", padx=5, pady=5)
        
        # Submit button
        self.submit_btn = ctk.CTkButton(
            button_frame,
            text="Submit Record",
            command=self.submit_record
        )
        self.submit_btn.pack(side="right", padx=5, pady=5)
        
        # Status label for feedback
        self.status_label = ctk.CTkLabel(self.scrollable_frame, text="")
        self.status_label.pack(fill="x", padx=10, pady=5)
        
    def create_progress_overlay(self):
        # Create a modal overlay frame (hidden by default)
        self.progress_overlay = ctk.CTkFrame(self, fg_color=("#000000", "#000000"), corner_radius=10)
        self.progress_overlay.place(relx=0.5, rely=0.5, anchor="center")
        self.progress_overlay.lower()  # Hide initially
        self.progress_label = ctk.CTkLabel(self.progress_overlay, text="Processing...", font=("Roboto", 16, "bold"))
        self.progress_label.pack(padx=20, pady=(20, 10))
        self.progress_bar = ctk.CTkProgressBar(self.progress_overlay, orientation="horizontal", mode="indeterminate", width=250)
        self.progress_bar.pack(padx=20, pady=(0, 20))
        self.progress_bar.configure(progress_color="#4283BD")

    def show_progress(self, message="Processing...", color="#4283BD", determinate=False):
        self.progress_label.configure(text=message)
        self.progress_bar.configure(progress_color=color)
        self.progress_overlay.lift()
        self.progress_overlay.place(relx=0.5, rely=0.5, anchor="center")
        if determinate:
            self.progress_bar.configure(mode="determinate")
            self.progress_bar.set(1.0)
        else:
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()
        self.update_idletasks()

    def hide_progress(self, delay=0):
        def _hide():
            self.progress_bar.stop()
            self.progress_overlay.lower()
            self.progress_overlay.place_forget()
        if delay > 0:
            self.after(delay, _hide)
        else:
            _hide()
        
    def upload_face_image(self):
        filetypes = (
            ('Image files', '*.png;*.jpg;*.jpeg'),
            ('All files', '*.*')
        )
        
        filename = filedialog.askopenfilename(
            title='Select Face Image',
            initialdir='/',
            filetypes=filetypes
        )
        
        if filename:
            self.face_image_path = filename
            messagebox.showinfo("Success", "Face image uploaded successfully!")
            
    def upload_additional_images(self):
        filetypes = (
            ('Image files', '*.png;*.jpg;*.jpeg'),
            ('All files', '*.*')
        )
        
        filenames = filedialog.askopenfilenames(
            title='Select Additional Images',
            initialdir='/',
            filetypes=filetypes
        )
        
        if filenames:
            self.additional_images = list(filenames)
            messagebox.showinfo("Success", f"{len(filenames)} additional images uploaded successfully!")
            
    def set_form_state(self, state):
        # state: "normal" or "disabled"
        widgets = [
            self.name_entry, self.dob_entry, self.height_entry, self.weight_entry,
            self.eye_color_entry, self.hair_color_entry, self.crimes_entry,
            self.status_entry, self.location_entry, self.notes_entry,
            self.face_image_btn, self.additional_images_btn, self.submit_btn
        ]
        for widget in widgets:
            widget.configure(state=state)
        
    def submit_record(self):
        self.status_label.configure(text="Processing face encodings...")
        self.set_form_state("disabled")
        self.show_progress("Encoding face(s)...", color="#4283BD")
        all_image_paths = [self.face_image_path] if self.face_image_path else []
        all_image_paths += self.additional_images

        def background_work():
            import face_recognition
            import numpy as np
            import cv2
            import os
            results = []
            for path in all_image_paths:
                try:
                    image = face_recognition.load_image_file(path)
                    # Use HOG model for fast face detection
                    face_locations = face_recognition.face_locations(image, model='hog')
                    # Use CNN model for accurate encoding
                    encodings = face_recognition.face_encodings(image, face_locations, model='cnn')
                    if encodings:
                        results.append((True, encodings[0], path))
                    else:
                        results.append((False, f'No face detected in {os.path.basename(path)}', path))
                except Exception as e:
                    results.append((False, str(e), path))
            errors = [msg for success, msg, path in results if not success]
            encodings = [(enc, path) for success, enc, path in results if success]
            if not encodings:
                self.after(0, lambda: [
                    self.status_label.configure(text="Face encoding error!"),
                    self.set_form_state("normal"),
                    self.show_progress(f"Error: {'; '.join(errors)}", color="#C0392B", determinate=True),
                    self.hide_progress(delay=1800)
                ])
                return
            try:
                self.after(0, lambda: self.show_progress("Uploading to database and images...", color="#4283BD"))
                data = {
                    'name': self.name_entry.get(),
                    'dob': self.dob_entry.get(),
                    'height': self.height_entry.get(),
                    'weight': self.weight_entry.get(),
                    'eye_color': self.eye_color_entry.get(),
                    'hair_color': self.hair_color_entry.get(),
                    'last_known_location': self.location_entry.get(),
                    'last_known_date': self.dob_entry.get(),
                    'status': self.status_entry.get(),
                    'notes': self.notes_entry.get("1.0", "end-1c")
                }
                logger.info("Attempting to add criminal record with data: %s", data)
                try:
                    response = add_criminal_record(data)
                except Exception as e:
                    self.after(0, lambda e=e: [
                        self.status_label.configure(text="Failed to add criminal record."),
                        self.set_form_state("normal"),
                        self.show_progress(f"Error: {str(e)}", color="#C0392B", determinate=True),
                        self.hide_progress(delay=1800)
                    ])
                    return
                if response and response.data:
                    criminal_id = response.data[0]['id']
                    for encoding, path in encodings:
                        encoding_bytes = np.array(encoding, dtype=np.float64).tobytes()
                        b64 = base64.b64encode(encoding_bytes).decode('utf-8')
                        print("Base64 encoding length:", len(b64), "First 100 chars:", b64[:100])
                        print("Actual encoding array for", os.path.basename(path), ":", encoding.tolist())
                        encoding_bytes = base64.b64decode(b64)
                        print("Decoded buffer length:", len(encoding_bytes))
                        supabase.table('face_encodings').insert({
                            'criminal_id': criminal_id,
                            'encoding': str(b64),
                            'source_image': os.path.basename(path)
                        }).execute()
                    # Upload and add face image (main)
                    try:
                        if self.face_image_path:
                            with open(self.face_image_path, 'rb') as f:
                                image_data = f.read()
                            filename = f"{criminal_id}_face{os.path.splitext(self.face_image_path)[1]}"
                            supabase.storage.from_('criminal-images').upload(
                                filename, 
                                image_data
                            )
                            image_url = supabase.storage.from_('criminal-images').get_public_url(filename)
                            image_response = supabase.table('criminal_images').insert({
                                'criminal_id': criminal_id,
                                'image_url': image_url,
                                'image_type': 'face'
                            }).execute()
                            logger.info("Face image added: %s", image_response)
                    except Exception as e:
                        logger.error("Error uploading face image: %s", str(e))
                        self.after(0, lambda: self.show_progress(f"Warning: Failed to upload face image", color="#F39C12", determinate=True))
                    # Upload and add additional images
                    for image_path in self.additional_images:
                        try:
                            with open(image_path, 'rb') as f:
                                image_data = f.read()
                            filename = f"{criminal_id}_additional_{os.path.basename(image_path)}"
                            supabase.storage.from_('criminal-images').upload(
                                filename, 
                                image_data
                            )
                            image_url = supabase.storage.from_('criminal-images').get_public_url(filename)
                            image_response = supabase.table('criminal_images').insert({
                                'criminal_id': criminal_id,
                                'image_url': image_url,
                                'image_type': 'additional'
                            }).execute()
                            logger.info("Additional image added: %s", image_response)
                        except Exception as e:
                            logger.error("Error uploading additional image: %s", str(e))
                            self.after(0, lambda path=image_path: self.show_progress(f"Warning: Failed to upload additional image: {path}", color="#F39C12", determinate=True))
                    self.after(0, lambda: [
                        self.status_label.configure(text="Record added successfully!"),
                        self.set_form_state("normal"),
                        self.show_progress("Success! Record added.", color="#27AE60", determinate=True),
                        self.clear_form(),
                        self.hide_progress(delay=1800)
                    ])
                else:
                    logger.error("Failed to add criminal record. Response: %s", response)
                    self.after(0, lambda: [
                        self.status_label.configure(text="Failed to add record."),
                        self.set_form_state("normal"),
                        self.show_progress("Error: Failed to add criminal record!", color="#C0392B", determinate=True),
                        self.hide_progress(delay=1800)
                    ])
            except Exception as e:
                logger.error("Error submitting record: %s", str(e), exc_info=True)
                self.after(0, lambda e=e: [
                    self.status_label.configure(text="An error occurred."),
                    self.set_form_state("normal"),
                    self.show_progress(f"Error: {str(e)}", color="#C0392B", determinate=True),
                    self.hide_progress(delay=1800)
                ])

        import threading
        threading.Thread(target=background_work, daemon=True).start()
        
    def clear_form(self):
        # Clear all entries
        self.name_entry.delete(0, "end")
        self.dob_entry.delete(0, "end")
        self.height_entry.delete(0, "end")
        self.weight_entry.delete(0, "end")
        self.eye_color_entry.delete(0, "end")
        self.hair_color_entry.delete(0, "end")
        self.crimes_entry.delete(0, "end")
        self.status_entry.delete(0, "end")
        self.location_entry.delete(0, "end")
        self.notes_entry.delete("1.0", "end")
        
        # Clear image paths
        self.face_image_path = None
        self.additional_images = []

if __name__ == "__main__":
    app = AddCriminalWindow()
    app.mainloop()