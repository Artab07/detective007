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

class AddCriminalWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

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
            
    def submit_record(self):
        try:
            # Validate required fields
            if not self.name_entry.get():
                messagebox.showerror("Error", "Name is required!")
                return
                
            if not self.face_image_path:
                messagebox.showerror("Error", "Face image is required!")
                return
                
            # Process face image and get encoding
            matcher = FaceMatcher()
            image = matcher.process_image(image_path=self.face_image_path)
            encodings = matcher.get_face_encodings(image)
            print("Face encodings:", encodings)

            if not encodings:
                messagebox.showerror("Error", "No face detected in the image!")
                return

            face_encoding = encodings[0]
            # Ensure dtype is float64
            face_encoding = face_encoding.astype(np.float64)
            print("[DEBUG] Encoding dtype:", face_encoding.dtype, "shape:", face_encoding.shape)

            # Compare with database
            matches = matcher.match_face(face_encoding)
            print("Matches from database:", matches)
            
            # Convert face encoding to base64 string for storage
            face_encoding_bytes = face_encoding.tobytes()
            face_encoding_base64 = base64.b64encode(face_encoding_bytes).decode('utf-8')

            # Prepare criminal record data
            data = {
                'name': self.name_entry.get(),
                'dob': self.dob_entry.get(),
                'height': self.height_entry.get(),
                'weight': self.weight_entry.get(),
                'eye_color': self.eye_color_entry.get(),
                'hair_color': self.hair_color_entry.get(),
                'last_known_location': self.location_entry.get(),
                'last_known_date': self.dob_entry.get(),  # Using DOB as last known date for now
                'status': self.status_entry.get(),
                'notes': self.notes_entry.get("1.0", "end-1c"),
                'face_encoding': face_encoding_base64
            }
            
            logger.info("Attempting to add criminal record with data: %s", data)
            
            # Add record to database
            response = add_criminal_record(data)
            
            if response and response.data:
                # Add images separately
                criminal_id = response.data[0]['id']
                
                # Upload and add face image
                try:
                    # Read the image file
                    with open(self.face_image_path, 'rb') as f:
                        image_data = f.read()
                    
                    # Generate a unique filename
                    filename = f"{criminal_id}_face{os.path.splitext(self.face_image_path)[1]}"
                    
                    # Upload to Supabase Storage
                    storage_response = supabase.storage.from_('criminal-images').upload(
                        filename, 
                        image_data
                    )
                    
                    # Get the public URL
                    image_url = supabase.storage.from_('criminal-images').get_public_url(filename)
                    
                    # Add face image record
                    image_response = supabase.table('criminal_images').insert({
                        'criminal_id': criminal_id,
                        'image_url': image_url,
                        'image_type': 'face'
                    }).execute()
                    logger.info("Face image added: %s", image_response)
                    
                except Exception as e:
                    logger.error("Error uploading face image: %s", str(e))
                    messagebox.showwarning("Warning", "Criminal record added but failed to upload face image")
                
                # Upload and add additional images
                for image_path in self.additional_images:
                    try:
                        # Read the image file
                        with open(image_path, 'rb') as f:
                            image_data = f.read()
                        
                        # Generate a unique filename
                        filename = f"{criminal_id}_additional_{os.path.basename(image_path)}"
                        
                        # Upload to Supabase Storage
                        storage_response = supabase.storage.from_('criminal-images').upload(
                            filename, 
                            image_data
                        )
                        
                        # Get the public URL
                        image_url = supabase.storage.from_('criminal-images').get_public_url(filename)
                        
                        # Add additional image record
                        image_response = supabase.table('criminal_images').insert({
                            'criminal_id': criminal_id,
                            'image_url': image_url,
                            'image_type': 'additional'
                        }).execute()
                        logger.info("Additional image added: %s", image_response)
                        
                    except Exception as e:
                        logger.error("Error uploading additional image: %s", str(e))
                        messagebox.showwarning("Warning", f"Failed to upload additional image: {image_path}")
                
                messagebox.showinfo("Success", "Criminal record added successfully!")
                self.clear_form()
            else:
                logger.error("Failed to add criminal record. Response: %s", response)
                messagebox.showerror("Error", "Failed to add criminal record!")
                
        except Exception as e:
            logger.error("Error submitting record: %s", str(e), exc_info=True)
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
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