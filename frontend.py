import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import tkinter.messagebox as tkmb
import os
from PIL import Image, ImageTk
import math
from datetime import datetime
import cv2
import logging
from face_matcher import FaceMatcher
from supabase_config import sign_in, sign_up, sign_out, get_current_user, add_criminal_record
import face_recognition
import numpy as np
import threading
from PIL import ImageGrab
import base64

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize global variables
middle_frame_right = None
sketch_canvas = None
face_matcher = FaceMatcher()
uploaded_image_path = None

# Add global progress overlay for matching/search
progress_overlay = None
progress_label = None
progress_bar = None

global current_user
current_user = None

class DraggableFeature:
    def __init__(self, canvas, image_path, initial_position=(0, 0)):
        self.canvas = canvas
        self.image_path = image_path
        
        # Load and store the original image with transparency
        self.original_image = Image.open(image_path)
        if self.original_image.mode != 'RGBA':
            self.original_image = self.original_image.convert('RGBA')
        
        # Initialize transformation values
        self.scale = 1.0
        self.rotation = 0
        self.position = initial_position
        
        # Create image on canvas
        self.update_image()
        
        # Create resize handles
        self.create_handles()
        
        # Bind mouse events
        self.rebind_events()

    def rebind_events(self):
        """Rebind all mouse events to ensure they work after updates"""
        self.canvas.tag_bind(self.id, '<Button-1>', self.on_press)
        self.canvas.tag_bind(self.id, '<B1-Motion>', self.on_drag)
        self.canvas.tag_bind(self.id, '<ButtonRelease-1>', self.on_release)
        self.canvas.tag_bind(self.id, '<Button-3>', self.show_context_menu)
    
    def create_handles(self):
        self.handles = []
        
        # Create resize handles at corners
        handle_positions = ['nw', 'ne', 'se', 'sw']
        for pos in handle_positions:
            handle = self.canvas.create_rectangle(0, 0, 8, 8,
                                               fill='white',
                                               outline='blue',
                                               tags=('handle', f'handle_{pos}'))
            self.handles.append(handle)
            
            # Bind events
            self.canvas.tag_bind(handle, '<Button-1>', lambda e, p=pos: self.start_resize(e, p))
            self.canvas.tag_bind(handle, '<B1-Motion>', self.on_resize)
            self.canvas.tag_bind(handle, '<ButtonRelease-1>', self.on_resize_complete)
        
        self.update_handles()
        self.hide_handles()
    
    def update_image(self):
        # Apply transformations
        image = self.original_image.copy()
        
        # Resize
        new_size = (
            int(image.width * self.scale),
            int(image.height * self.scale)
        )
        image = image.resize(new_size, Image.LANCZOS)
        
        # Rotate
        image = image.rotate(self.rotation, expand=True, resample=Image.BICUBIC)
        
        # Use ImageTk.PhotoImage for Tkinter Canvas
        self.image = ImageTk.PhotoImage(image)
        
        # --- Keep a reference to all images to prevent garbage collection ---
        if not hasattr(self, '_image_refs'):
            self._image_refs = []
        self._image_refs.append(self.image)
        
        # Update or create canvas image
        if hasattr(self, 'id'):
            # Store the current position before deleting
            current_pos = self.position
            self.canvas.delete(self.id)
            # Restore the position
            self.position = current_pos
        
        self.id = self.canvas.create_image(
            self.position[0], self.position[1],
            image=self.image,
            anchor='center',
            tags='feature'
        )
        
        # Rebind events after updating image
        self.rebind_events()
        
        # Update handles
        if hasattr(self, 'handles'):
            self.update_handles()
    
    def update_handles(self):
        bbox = self.canvas.bbox(self.id)
        if not bbox:
            return
            
        # Get center and dimensions
        cx, cy = (bbox[0] + bbox[2])/2, (bbox[1] + bbox[3])/2
        width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        # Update handle positions
        positions = {
            'nw': (bbox[0], bbox[1]),
            'ne': (bbox[2], bbox[1]),
            'se': (bbox[2], bbox[3]),
            'sw': (bbox[0], bbox[3])
        }
        
        for handle, pos in zip(self.handles, positions.values()):
            self.canvas.coords(handle, 
                             pos[0]-4, pos[1]-4,
                             pos[0]+4, pos[1]+4)
            # Ensure handles stay above the image
            self.canvas.tag_raise(handle, self.id)
    
    def show_handles(self):
        for handle in self.handles:
            self.canvas.itemconfig(handle, state='normal')
            self.canvas.tag_raise(handle, self.id)
    
    def hide_handles(self):
        for handle in self.handles:
            self.canvas.itemconfig(handle, state='hidden')
    
    def on_press(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.start_pos = self.position
        
        # Show handles
        self.show_handles()
    
    def on_drag(self, event):
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        self.position = (self.start_pos[0] + dx, self.start_pos[1] + dy)
        self.canvas.coords(self.id, self.position[0], self.position[1])
        self.update_handles()
    
    def on_release(self, event):
        # Update the starting position for next drag
        self.start_pos = self.position
    
    def start_resize(self, event, handle_pos):
        self.resize_start = (event.x, event.y)
        self.resize_start_scale = self.scale
        self.resize_handle = handle_pos
        # Store current position
        self.resize_start_pos = self.position
    
    def on_resize(self, event):
        if not hasattr(self, 'resize_start'):
            return
            
        # Calculate distance moved
        dx = event.x - self.resize_start[0]
        dy = event.y - self.resize_start[1]
        
        # Calculate new scale based on diagonal movement
        distance = math.sqrt(dx**2 + dy**2)
        direction = 1 if dx + dy > 0 else -1
        
        # Update scale
        self.scale = self.resize_start_scale * (1 + direction * distance/100)
        self.scale = max(0.1, min(3.0, self.scale))  # Limit scale range
        
        # Preserve position during resize
        self.position = self.resize_start_pos
        
        # Update image
        self.update_image()
    
    def on_resize_complete(self, event):
        if hasattr(self, 'resize_start'):
            delattr(self, 'resize_start')
    
    def show_context_menu(self, event):
        menu = tk.Menu(self.canvas, tearoff=0)
        
        # Add rotation options
        menu.add_command(label="Rotate Left", 
                        command=lambda: self.rotate(-15))
        menu.add_command(label="Rotate Right", 
                        command=lambda: self.rotate(15))
        
        # Add layer options
        menu.add_separator()
        menu.add_command(label="Bring to Front", 
                        command=self.bring_to_front)
        menu.add_command(label="Send to Back", 
                        command=self.send_to_back)
        
        # Delete option
        menu.add_separator()
        menu.add_command(label="Delete", 
                        command=self.delete)
        
        menu.tk_popup(event.x_root, event.y_root)
    
    def rotate(self, angle):
        self.rotation = (self.rotation + angle) % 360
        self.update_image()
    
    def bring_to_front(self):
        # Raise the image above all other features
        self.canvas.tag_raise(self.id)
        # Raise the handles above the image
        for handle in self.handles:
            self.canvas.tag_raise(handle)
    
    def send_to_back(self):
        # Find all feature items
        all_features = self.canvas.find_withtag('feature')
        if len(all_features) > 1:
            # Get the bottom-most feature
            bottom_feature = min(all_features)
            # Move current feature below it
            self.canvas.tag_lower(self.id, bottom_feature)
            # Keep handles above the image but below other features
            for handle in self.handles:
                self.canvas.tag_raise(handle, self.id)
    
    def delete(self):
        self.canvas.delete(self.id)
        for handle in self.handles:
            self.canvas.delete(handle)


class SketchCanvas(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Create canvas with white background
        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.pack(fill="both", expand=True)
        
        self.features = []
        
        # Bind canvas click to deselect
        self.canvas.bind('<Button-1>', self.deselect_all)
    
    def add_feature(self, image_path):
        # Get canvas center
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        center = (canvas_width//2, canvas_height//2)
        
        # Create new feature
        feature = DraggableFeature(self.canvas, image_path, center)
        self.features.append(feature)
        return feature
    
    def deselect_all(self, event=None):
        if event and self.canvas.find_withtag('current'):
            return
        for feature in self.features:
            feature.hide_handles()
    
    def clear_canvas(self):
        self.canvas.delete('all')
        self.features.clear()
    
    def delete_last_shape(self):
        if self.features:
            last_feature = self.features.pop()  # Remove last feature from list
            last_feature.delete()  # Delete from canvas
            return True
        return False


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.geometry("1200x700")
root.title("Detective 007")

def show_welcome_screen():
    # Clear the current contents of the window
    for widget in root.winfo_children():
        widget.destroy()
    
    # Create the main frame
    frame = ctk.CTkFrame(master=root)
    frame.pack(fill="both", expand=True)

    # Load and create the background image
    bg_image = Image.open("images/Detective_007.jpg")
    bg_photo = ctk.CTkImage(bg_image, size=(1200, 700))

    # Create a label with the background image
    bg_label = ctk.CTkLabel(frame, image=bg_photo, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Create a semi-transparent overlay frame
    overlay_frame = ctk.CTkFrame(frame, fg_color="transparent", bg_color="transparent")
    overlay_frame.configure(fg_color="transparent")
    overlay_frame.configure(bg_color="transparent")
    overlay_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.4, relheight=0.1)

    # Sign In button
    sign_in_button = ctk.CTkButton(overlay_frame,
                                   text="Sign In",
                                   command=show_login_screen,
                                   fg_color="#597276",  
                                   hover_color="#2B3C43")
    sign_in_button.place(relx=0.3, rely=0.5, anchor="center")

    # Sign Up button
    sign_up_button = ctk.CTkButton(overlay_frame,
                                   text="Sign Up",
                                   command=show_signup_screen,
                                   fg_color="#597276",  
                                   hover_color="#2B3C43")
    sign_up_button.place(relx=0.7, rely=0.5, anchor="center")



def show_login_screen():
    # Clear the current contents of the window
    for widget in root.winfo_children():
        widget.destroy()
    
    frame = ctk.CTkFrame(master=root)
    frame.pack(pady=20, padx=60, fill="both", expand=True)

    # Update the window title
    root.title("Detective 007 Login")

    # Add back arrow button
    back_button = ctk.CTkButton(master=frame, text="←", command=show_welcome_screen, width=50,
                            fg_color="transparent",
                            text_color="white",
                            hover_color="#4283BD",
                            text_color_disabled="gray")
    back_button.pack(anchor="nw", padx=10, pady=10)
    
    # Recreate the login screen
    label = ctk.CTkLabel(master=frame, text="Login System", font=("Roboto", 24))
    label.pack(pady=20, padx=10)

    global user_email_entry, user_pass, role_var
    # Add role dropdown ABOVE email field
    role_var = tk.StringVar(value="Public")
    role_label = ctk.CTkLabel(master=frame, text="Select Role:")
    role_label.pack(pady=(10, 0))
    role_dropdown = ctk.CTkOptionMenu(master=frame, variable=role_var, values=["Admin", "Public"])
    role_dropdown.pack(pady=8)

    user_email_entry = ctk.CTkEntry(master=frame, placeholder_text="Email")
    user_email_entry.pack(pady=12, padx=10)

    user_pass = ctk.CTkEntry(master=frame, placeholder_text="Password", show="*")
    user_pass.pack(pady=12, padx=10)

    button = ctk.CTkButton(master=frame, text="Login", command=handle_login)
    button.pack(pady=12, padx=10)
    checkbox = ctk.CTkCheckBox(master=frame, text="Remember Me")
    checkbox.pack(pady=12, padx=10)

def show_signup_screen():
    # Clear the current contents of the window
    for widget in root.winfo_children():
        widget.destroy()
    
    frame = ctk.CTkFrame(master=root)
    frame.pack(pady=20, padx=60, fill="both", expand=True)

    # Update the window title
    root.title("Detective 007 Sign Up")

    # Add back arrow button
    back_button = ctk.CTkButton(frame, text="←", command=show_welcome_screen, width=50,
                            fg_color="transparent",
                            text_color="white",
                            hover_color="#4283BD",
                            text_color_disabled="gray")
    back_button.pack(anchor="nw", padx=10, pady=10)
    
    # Recreate the sign up screen
    label = ctk.CTkLabel(master=frame, text="Sign Up to Investigate", font=("Roboto", 24))
    label.pack(pady=20, padx=10)

    global signup_email_entry, signup_pass_entry, signup_pass_confirm_entry
    signup_email_entry = ctk.CTkEntry(master=frame, placeholder_text="Email")
    signup_email_entry.pack(pady=12, padx=10)

    signup_pass_entry = ctk.CTkEntry(master=frame, placeholder_text="Password", show="*")
    signup_pass_entry.pack(pady=12, padx=10)

    signup_pass_confirm_entry = ctk.CTkEntry(master=frame, placeholder_text="Re-enter Password", show="*")
    signup_pass_confirm_entry.pack(pady=12, padx=10)

    button = ctk.CTkButton(master=frame, text="Sign Up", command=handle_signup)
    button.pack(pady=12, padx=10)
    note = ctk.CTkLabel(master=frame, text="After signing up, check your email for a confirmation link.\nYou may see a browser error—this is normal. Just return to the app and log in.", font=("Roboto", 10), text_color="gray")
    note.pack(pady=5)

def handle_login():
    global current_user
    email = user_email_entry.get()
    password = user_pass.get()
    try:
        response = sign_in(email, password)
        if hasattr(response, 'error') and response.error:
            if 'Email not confirmed' in str(response.error):
                tkmb.showerror("Login Failed", "Please confirm your email before logging in. Check your inbox and spam folder.")
            else:
                tkmb.showerror("Login Failed", f"Error: {response.error}")
            return
        if hasattr(response, 'user') and response.user:
            current_user = response.user
            show_premain_screen()
        else:
            tkmb.showerror("Login Failed", "Invalid email or password.")
    except Exception as e:
        tkmb.showerror("Login Failed", f"Error: {str(e)}")

def handle_signup():
    email = signup_email_entry.get()
    password = signup_pass_entry.get()
    confirm = signup_pass_confirm_entry.get()
    if not email or not password or not confirm:
        tkmb.showerror("Error", "All fields are required.")
        return
    if password != confirm:
        tkmb.showerror("Error", "Passwords do not match.")
        return
    try:
        response = sign_up(email, password, None)
        # Check for error in response
        if hasattr(response, 'error') and response.error:
            if 'User already registered' in str(response.error):
                tkmb.showerror("Sign Up Failed", "This email is already registered. Please log in or use a different email.")
            else:
                tkmb.showerror("Sign Up Failed", f"Error: {response.error}")
            return
        if hasattr(response, 'user') and response.user:
            tkmb.showinfo(
                "Success",
                "Sign up successful! Please check your email to confirm your account before logging in.\n\nYou may see a 'site can't be reached' error—this is normal. After confirming, return to the app and log in."
            )
            show_login_screen()
        else:
            tkmb.showerror("Sign Up Failed", "Could not create account. Try again.")
    except Exception as e:
        tkmb.showerror("Sign Up Failed", f"Error: {str(e)}")

def show_premain_screen():
    # Clear the current contents of the window
    for widget in root.winfo_children():
        widget.destroy()
    
    frame = ctk.CTkFrame(master=root)
    frame.pack(pady=20, padx=60, fill="both", expand=True)
    
    # Update the window title
    root.title("Detective 007 - Choose")
    
    # Add back arrow button
    back_button = ctk.CTkButton(frame, text="←", 
                               command=show_login_screen, 
                               width=50,
                               fg_color="transparent",
                               text_color="white",
                               hover_color="#4283BD",
                               text_color_disabled="gray")
    back_button.pack(anchor="nw", padx=10, pady=10)
    
    # Recreate the before main screen
    label = ctk.CTkLabel(master=frame, text="Create Sketch / Upload Sketch", font=("Roboto", 24))
    label.pack(pady=20, padx=10)
    
    # Show buttons based on role
    global role_var
    role = role_var.get() if 'role_var' in globals() else "Public"
    button = ctk.CTkButton(master=frame, text="Create Sketch", command=show_main_screen)
    button.pack(pady=12, padx=10)
    upload_button = ctk.CTkButton(master=frame, text="Upload Sketch", command=show_premain_screen_2)
    upload_button.pack(pady=12, padx=10)
    if role == "Admin":
        # Add Criminal Record button for Admin
        add_criminal_btn = ctk.CTkButton(master=frame, text="Add Criminal Record", fg_color="#4283BD", hover_color="#2B3C43", command=show_add_criminal_screen)
        add_criminal_btn.pack(pady=12, padx=10)


def show_premain_screen_2(preview_path=None):
    global left_frame, middle_frame, right_frame, upload_button1, button_frame, uploaded_image_path
    # Clear the current contents of the window
    for widget in root.winfo_children():
        widget.destroy()
    
    # Update the window title
    root.title("Detective 007 - Upload or take picture")


    # Create main frame
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Configure rows and columns for resizing
    main_frame.grid_columnconfigure(0, weight=1)  # 1st row Back arrow frame
    main_frame.grid_rowconfigure(1, weight=5)  # 2nd row (for frames) gets more weight
    main_frame.grid_rowconfigure(2, weight=1)  # 3rd row (for buttons) gets less weight
    main_frame.grid_columnconfigure(0, weight=5)
    main_frame.grid_columnconfigure(1, weight=5)
    main_frame.grid_columnconfigure(2, weight=2)


    # Create a frame for back button in the 1st row
    back_arrow_frame = ctk.CTkFrame(main_frame)
    back_arrow_frame.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="ew")

    # Add back arrow button
    back_button = ctk.CTkButton(back_arrow_frame, text="←", 
                               command=show_login_screen, 
                               width=50,
                               fg_color="transparent",
                               text_color="white",
                               hover_color="#4283BD",
                               text_color_disabled="gray")
    back_button.pack(side="left", padx=10, pady=10)

    # Add Clear button at the right corner of the top frame
    def clear_upload_screen_fields():
        global uploaded_image_path
        # Clear left_frame (image preview)
        for widget in left_frame.winfo_children():
            widget.destroy()
        uploaded_image_path = None
        # Optionally clear other fields if needed
    clear_btn = ctk.CTkButton(back_arrow_frame, text="Clear", command=clear_upload_screen_fields, fg_color="#56666F", hover_color="#314048")
    clear_btn.pack(side="right", padx=10, pady=10)

    # Left column (now in 2nd row)
    left_frame = ctk.CTkFrame(main_frame)
    left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # Middle column (now in 2nd row)
    middle_frame = ctk.CTkFrame(main_frame)
    middle_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    # Right column (now in 2nd row)
    right_frame = ctk.CTkFrame(main_frame)
    right_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

    # Create a frame for buttons in the 3rd row
    button_frame = ctk.CTkFrame(main_frame)
    button_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky="ew")

    # Create buttons with grid layout

    # Button definitions
    upload_button1 = ctk.CTkButton(master=button_frame, text="Capture Image", command=capture_image)
    upload_button1.grid(row=0, column=0, padx=70)

    upload_button2 = ctk.CTkButton(master=button_frame, text="Upload Sketch", command=upload_sketch)
    upload_button2.grid(row=0, column=1, padx=70)

    upload_button3 = ctk.CTkButton(master=button_frame, text="Submit Image", command=submit_image)
    upload_button3.grid(row=0, column=2, padx=70)

    upload_button4 = ctk.CTkButton(master=button_frame, text="Logout", command=show_login_screen, fg_color="#C0392B", hover_color="#9D0B28")
    upload_button4.grid(row=0, column=3, padx=70)

    # Configure button_frame columns to distribute space evenly
    button_frame.grid_columnconfigure((0,1,2,3), weight=1)

    # Preview the sketch if a path is provided
    if preview_path and os.path.exists(preview_path):
        from PIL import Image
        img = Image.open(preview_path)
        preview_size = (250, 250)
        img.thumbnail(preview_size, Image.LANCZOS)
        photo = ctk.CTkImage(img, size=preview_size)
        img_label = ctk.CTkLabel(left_frame, image=photo, text="")
        img_label.image = photo
        img_label.pack(expand=True, pady=20)
        uploaded_image_path = preview_path  # Set for submit_image
        print(f"[DEBUG] Previewing and setting uploaded_image_path: {uploaded_image_path}")

def capture_image():
    """Open the webcam and show the live feed inside left_frame with buttons remaining."""
    global cap, left_label, take_picture_btn, close_camera_btn, upload_button1, btn_frame

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        tkmb.showerror("Error", "Could not access the camera")
        return

    # Disable "Capture Image" button
    upload_button1.configure(state="disabled")

    # Clear previous widgets inside left_frame (including old labels but NOT the button frame)
    for widget in left_frame.winfo_children():
        widget.destroy()

    # Label for displaying live feed
    left_label = ctk.CTkLabel(left_frame, text="")
    left_label.pack(fill="both", expand=True)

    def show_frame():
        """Capture frames and update the label."""
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                ctk_img = ctk.CTkImage(img, size=img.size)
                left_label.configure(image=ctk_img)
                left_label.image = ctk_img
            left_label.after(10, show_frame)

    show_frame()  # Start the live feed

    # Recreate the button frame every time Capture Image is clicked
    btn_frame = ctk.CTkFrame(left_frame, fg_color="#23272E", corner_radius=16)
    btn_frame.pack(side="bottom", fill="x", pady=20, padx=20)

    # "Take Picture" button without emoji
    take_picture_btn = ctk.CTkButton(
        btn_frame, text="Take Picture", command=take_picture,
        fg_color="#4283BD", hover_color="#2B3C43", corner_radius=12, font=("Roboto", 14, "bold"), width=140, height=40
    )
    take_picture_btn.pack(side="left", padx=20, pady=10)

    # "Close Camera" button without emoji
    close_camera_btn = ctk.CTkButton(
        btn_frame, text="Close Camera", command=close_camera,
        fg_color="#C0392B", hover_color="#9D0B28", corner_radius=12, font=("Roboto", 14, "bold"), width=140, height=40
    )
    close_camera_btn.pack(side="right", padx=20, pady=10)


def take_picture():
    """Capture a single frame, save it, and display it inside left_frame while keeping buttons visible."""
    global cap, left_label, take_picture_btn, captured_label

    if cap is None or not cap.isOpened():
        tkmb.showerror("Error", "Camera is not active")
        return

    ret, frame = cap.read()
    if ret:
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)

        # Save the captured image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"captured_image_{timestamp}.png"
        img.save(filename)

        # Stop live feed and clear only the live feed label
        if left_label:
            left_label.pack_forget()

        # Display the captured image inside left_frame
        captured_img = ImageTk.PhotoImage(image=img)

        # If an old captured image exists, replace it
        if "captured_label" in globals():
            captured_label.configure(image=captured_img)
            captured_label.image = captured_img
        else:
            captured_label = ctk.CTkLabel(left_frame, image=captured_img, text="")
            captured_label.image = captured_img  # Keep reference
            captured_label.pack(fill="both", expand=True)

        # Disable "Take Picture" button after capturing
        take_picture_btn.configure(state="disabled")

        tkmb.showinfo("Success", f"Image saved as {filename}")

    else:
        tkmb.showerror("Error", "Failed to capture image")


def close_camera():
    """Close the camera and restore left_frame to normal."""
    global cap, left_label, upload_button1, take_picture_btn, btn_frame, uploaded_image_path

    if cap:
        cap.release()

    # Clear everything inside left_frame (including buttons)
    for widget in left_frame.winfo_children():
        widget.destroy()

    # Re-enable "Capture Image" button
    upload_button1.configure(state="normal")

    # Restore preview image if available, else show placeholder
    if uploaded_image_path and os.path.exists(uploaded_image_path):
        from PIL import Image
        img = Image.open(uploaded_image_path)
        preview_size = (250, 250)
        img.thumbnail(preview_size, Image.LANCZOS)
        photo = ctk.CTkImage(img, size=preview_size)
        img_label = ctk.CTkLabel(left_frame, image=photo, text="")
        img_label.image = photo
        img_label.pack(expand=True, pady=20)
    else:
        # Show a placeholder to maintain frame size
        placeholder = ctk.CTkLabel(left_frame, text="No image preview", width=250, height=250)
        placeholder.pack(expand=True, pady=20)



def upload_sketch():
    """Handle sketch upload from file system"""
    global uploaded_image_path
    filetypes = (
        ('Image files', '*.png;*.jpg;*.jpeg'),
        ('All files', '*.*')
    )
    
    filename = filedialog.askopenfilename(
        title='Upload Sketch',
        initialdir='/',
        filetypes=filetypes
    )
    
    if filename:
        try:
            # Clear previous widgets inside left_frame
            for widget in left_frame.winfo_children():
                widget.destroy()
                
            # Load and display the image
            img = Image.open(filename)
            
            # Set a fixed preview size
            preview_size = (250, 250)
            img.thumbnail(preview_size, Image.LANCZOS)
            
            # Convert to CTkImage
            photo = ctk.CTkImage(img, size=preview_size)
            
            # Create label and display image, center in frame
            img_label = ctk.CTkLabel(left_frame, image=photo, text="")
            img_label.image = photo  # Keep a reference
            img_label.pack(expand=True, pady=20)
            
            # Store the uploaded image path for later submission
            uploaded_image_path = filename
            tkmb.showinfo("Success", "Sketch uploaded successfully! Now click Submit to search for matches.")
        except Exception as e:
            tkmb.showerror("Error", f"Failed to upload sketch: {str(e)}")

def submit_image():
    global uploaded_image_path
    print(f"[DEBUG] Submitting image: {uploaded_image_path}")
    if not uploaded_image_path:
        tkmb.showwarning("Warning", "No image to submit. Please upload an image first.")
        return
    try:
        process_image(uploaded_image_path)
    except Exception as e:
        tkmb.showerror("Error", f"Failed to process image: {str(e)}")

def create_progress_overlay(parent):
    global progress_overlay, progress_label, progress_bar
    if progress_overlay is not None:
        return
    progress_overlay = ctk.CTkFrame(parent, fg_color=("#000000", "#000000"), corner_radius=10)
    progress_overlay.place(relx=0.5, rely=0.5, anchor="center")
    progress_overlay.lower()  # Hide initially
    progress_label = ctk.CTkLabel(progress_overlay, text="Processing...", font=("Roboto", 16, "bold"))
    progress_label.pack(padx=20, pady=(20, 10))
    progress_bar = ctk.CTkProgressBar(progress_overlay, orientation="horizontal", mode="indeterminate", width=250)
    progress_bar.pack(padx=20, pady=(0, 20))
    progress_bar.configure(progress_color="#4283BD")

def show_progress(message="Processing...", color="#4283BD", determinate=False):
    global progress_overlay, progress_label, progress_bar
    if progress_overlay is None:
        create_progress_overlay(root)
    progress_label.configure(text=message)
    progress_bar.configure(progress_color=color)
    progress_overlay.lift()
    progress_overlay.place(relx=0.5, rely=0.5, anchor="center")
    if determinate:
        progress_bar.configure(mode="determinate")
        progress_bar.set(1.0)
    else:
        progress_bar.configure(mode="indeterminate")
        progress_bar.start()
    root.update_idletasks()

def hide_progress(delay=0):
    global progress_overlay, progress_bar
    def _hide():
        progress_bar.stop()
        progress_overlay.lower()
        progress_overlay.place_forget()
    if delay > 0:
        root.after(delay, _hide)
    else:
        _hide()

def process_image(image_path):
    show_progress("Encoding face...", color="#4283BD")  # Show loader immediately
    def background_work():
        try:
            face_encodings = []
            try:
                from PIL import Image as PILImage
                image = face_recognition.load_image_file(image_path)
                pil_img = PILImage.fromarray(image)
                pil_img.thumbnail((600, 600), PILImage.LANCZOS)
                image = np.array(pil_img)
                face_locations = face_recognition.face_locations(image, model='cnn')
                print(f"[DEBUG] Detected {len(face_locations)} faces at: {face_locations} in {os.path.basename(image_path)}")
                if len(face_locations) == 0:
                    PILImage.fromarray(image).save(f"debug_no_face_{os.path.basename(image_path)}.jpg")
                face_encodings = face_recognition.face_encodings(image, face_locations, model='cnn')
            except Exception as e:
                logger.error(f"Error in face detection/encoding: {str(e)}")
            if not face_encodings:
                root.after(0, lambda: [show_progress("No faces detected in the image.", color="#C0392B", determinate=True), hide_progress(delay=1800)])
                return
            root.after(0, lambda: show_progress("Searching database for matches...", color="#4283BD"))
            best_match = None
            best_distance = 1e9
            for encoding in face_encodings:
                print(f"[DEBUG] Encoding for matching (frontend): {encoding.tolist()}")
                match_results = face_matcher.match_face(encoding, tolerance=0.75)
                if match_results:
                    match = match_results[0]
                    if 'distance' in match and match['distance'] < best_distance:
                        best_match = match
                        best_distance = match['distance']
            if not best_match:
                root.after(0, lambda: [show_progress("No matching records found.", color="#C0392B", determinate=True), hide_progress(delay=1800)])
                return
            root.after(0, lambda: [show_progress("Match found! Displaying result...", color="#27AE60", determinate=True), root.after(1200, lambda: [hide_progress(), display_best_match_in_frames(best_match)])])
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            root.after(0, lambda: [show_progress(f"Error: {str(e)}", color="#C0392B", determinate=True), hide_progress(delay=1800)])
    threading.Thread(target=background_work, daemon=True).start()

# Helper to clear a frame
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def display_best_match_in_frames(match):
    global right_frame, middle_frame
    # --- Update right_frame with details ---
    clear_frame(right_frame)
    details = [
        ("Name", match.get('name', 'Unknown')),
        ("ID", match.get('id', 'Unknown')),
        ("Matching Score", f"{1 - match.get('distance', 1):.2%}"),
        ("Date of Birth", match.get('dob', 'Unknown')),
        ("Height", match.get('height', 'Unknown')),
        ("Weight", match.get('weight', 'Unknown')),
        ("Eye Color", match.get('eye_color', 'Unknown')),
        ("Hair Color", match.get('hair_color', 'Unknown')),
        ("Last Known Location", match.get('last_known_location', 'Unknown')),
        ("Last Known Date", match.get('last_known_date', 'Unknown')),
        ("Status", match.get('status', 'Unknown')),
        ("Notes", match.get('notes', 'No additional notes'))
    ]
    for label, value in details:
        frame = ctk.CTkFrame(right_frame)
        frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(frame, text=f"{label}:").pack(side="left", padx=10)
        ctk.CTkLabel(frame, text=str(value)).pack(side="left", padx=10)

    # --- Update middle_frame with the best match's image ---
    clear_frame(middle_frame)
    # Try to get the image_url from match, or fetch from DB if not present
    image_url = match.get('image_url')
    if not image_url:
        # Try to fetch from supabase criminal_images table (face type)
        try:
            from supabase_config import supabase
            images = supabase.table('criminal_images').select('*').eq('criminal_id', match.get('id')).eq('image_type', 'face').execute()
            if images.data and len(images.data) > 0:
                image_url = images.data[0]['image_url']
        except Exception as e:
            logger.error(f"Error fetching image from DB: {str(e)}")
    if image_url:
        try:
            import requests
            from io import BytesIO
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
            img = img.resize((300, 300), Image.LANCZOS)
            photo = ctk.CTkImage(img, size=(300, 300))
            img_label = ctk.CTkLabel(middle_frame, image=photo, text="")
            img_label.image = photo
            img_label.pack(pady=20)
        except Exception as e:
            logger.error(f"Error loading/displaying image: {str(e)}")
            ctk.CTkLabel(middle_frame, text="Image not available").pack(pady=20)
    else:
        ctk.CTkLabel(middle_frame, text="Image not available").pack(pady=20)

def submit_sketch():
    try:
        import os
        from datetime import datetime
        from PIL import ImageGrab
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(downloads_dir):
            downloads_dir = "."
        sketch_path = os.path.join(downloads_dir, f"sketch_{timestamp}.png")
        x = sketch_canvas.winfo_rootx()
        y = sketch_canvas.winfo_rooty()
        x1 = x + sketch_canvas.winfo_width()
        y1 = y + sketch_canvas.winfo_height()
        ImageGrab.grab().crop((x, y, x1, y1)).save(sketch_path)
        print(f"[DEBUG] Sketch saved to: {sketch_path}")
        show_premain_screen_2(preview_path=sketch_path)
    except Exception as e:
        logger.error(f"Error submitting sketch: {str(e)}")
        tkmb.showerror("Error", f"An error occurred while submitting the sketch: {str(e)}")

def clear_middle_frame_right():
    global middle_frame_right
    if middle_frame_right:
        for widget in middle_frame_right.winfo_children():
            widget.destroy()

def show_main_screen():
    # Clear the current contents of the window
    for widget in root.winfo_children():
        widget.destroy()
    
    # Update the window title
    root.title("Detective 007 - Main Screen")
    
    # Create main frame
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(pady=20, padx=20, fill="both", expand=True)
    
    # Configure rows and columns for resizing
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=0)
    main_frame.grid_columnconfigure(1, weight=10)
    main_frame.grid_columnconfigure(2, weight=3)
    
    # Left column (dashboard)
    left_frame = ctk.CTkFrame(main_frame)
    left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    left_frame.grid_rowconfigure(0, weight=1)

    # Right column
    global right_frame, middle_frame, middle_frame_right, sketch_canvas
    right_frame = ctk.CTkFrame(main_frame)
    right_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
    
    # Middle column
    middle_frame = ctk.CTkFrame(main_frame)
    middle_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    
    # Create SketchCanvas in middle frame
    sketch_canvas = SketchCanvas(middle_frame)
    sketch_canvas.pack(fill="both", expand=True, padx=10, pady=10)

    # Divide right frame into 3 parts
    # 1. Top part for logout button
    top_frame = ctk.CTkFrame(right_frame)
    top_frame.pack(side="top", fill="x", padx=5, pady=5)

    def delete_shape():
        if sketch_canvas.delete_last_shape():
            print("Shape Deleted")
        else:
            print("No shapes to delete")

    delete_shape_btn = ctk.CTkButton(top_frame, text="Delete Shape", command=delete_shape, 
                             fg_color="#56666F", hover_color="#314048")
    delete_shape_btn.pack(side="left", padx=5, pady=5)
    
    logout_btn = ctk.CTkButton(top_frame, text="Logout", command=show_welcome_screen, 
                              fg_color="#FF0000", hover_color="#9D0B28")
    logout_btn.pack(side="right", padx=5, pady=5)
    
    # 2. Middle part for displaying images
    middle_frame_right = ctk.CTkFrame(right_frame)
    middle_frame_right.pack(side="top", fill="both", expand=True, padx=5, pady=5)

    # Image display area in the right column
    image_label = ctk.CTkLabel(middle_frame_right, text="Select a facial element", width=200, height=200)
    image_label.pack(pady=20)
    
    # 3. Bottom part for buttons
    bottom_frame = ctk.CTkFrame(right_frame)
    bottom_frame.pack(side="bottom", fill="x", padx=5, pady=5)
    
    clear_btn = ctk.CTkButton(bottom_frame, text="Clear Canvas", command=sketch_canvas.clear_canvas, 
                             fg_color="#56666F", hover_color="#314048")
    clear_btn.pack(side="left", padx=5, pady=5)
    
    # Use the global submit_sketch function
    submit_btn = ctk.CTkButton(bottom_frame, text="Submit Sketch", command=submit_sketch, 
                              fg_color="#522377", hover_color="#36195B")
    submit_btn.pack(side="right", padx=5, pady=5)
    
    # Add facial element buttons to left_frame
    facial_elements = ["Head", "Hair", "Neck", "Nose", "Eyes", "Eyebrows", "Lips", "Moustache", "Ears"]
    for element in facial_elements:
        button = ctk.CTkButton(left_frame, text=element, 
                              command=lambda e=element: show_facial_element(e),
                              fg_color="#016764", hover_color="#014848")
        button.pack(anchor="n", padx=5, pady=5)



def show_facial_element(element):
    element_folder = element.lower()
    if element_folder == "moustache":
        element_folder = "mustach"
    image_folder = os.path.join("face_features", element_folder)
    print(f"Searching for images in: {image_folder}")
    
    if os.path.exists(image_folder) and os.path.isdir(image_folder):
        image_files = [f for f in os.listdir(image_folder) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        if image_files:
            display_image_matrix(image_files, image_folder, element)
        else:
            print(f"No image files found in {image_folder}")
            clear_middle_frame_right()
            ctk.CTkLabel(middle_frame_right, text=f"No images for {element}").pack(pady=20)
    else:
        print(f"Folder not found: {image_folder}")
        clear_middle_frame_right()
        ctk.CTkLabel(middle_frame_right, text=f"No folder for {element}").pack(pady=20)

def display_image_matrix(image_files, image_folder, element):
    global middle_frame_right, sketch_canvas
    clear_middle_frame_right()
    
    scrollable_frame = ctk.CTkScrollableFrame(middle_frame_right)
    scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create grid layout
    row = 0
    col = 0
    max_cols = 2
    image_size = (150, 150)
    
    label = ctk.CTkLabel(scrollable_frame, text=f"Selected: {element}")
    label.grid(row=row, column=0, columnspan=max_cols, pady=10)
    row += 1
    
    for file in image_files:
        image_path = os.path.join(image_folder, file)
        img = Image.open(image_path)
        
        # Convert to RGBA for display purposes only
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # For display in the selection panel only, add white background
        background = Image.new('RGBA', img.size, (255, 255, 255, 255))
        composite = Image.alpha_composite(background, img)
        composite = composite.convert('RGB')
        composite = composite.resize(image_size, Image.LANCZOS)
        
        photo = ctk.CTkImage(composite, size=image_size)
        
        image_frame = ctk.CTkFrame(scrollable_frame, fg_color="white")
        image_frame.grid(row=row, column=col, padx=5, pady=5)
        
        image_button = ctk.CTkButton(
            image_frame,
            image=photo,
            text="",
            width=image_size[0],
            height=image_size[1],
            fg_color="white",
            hover_color="#4283BD",
            command=lambda path=image_path: sketch_canvas.add_feature(path)
        )
        image_button.pack(padx=2, pady=2)
        
        col += 1
        if col == max_cols:
            col = 0
            row += 1
    
    for i in range(max_cols):
        scrollable_frame.grid_columnconfigure(i, weight=1)

def show_add_criminal_screen():
    # Clear the current contents of the window
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Add Criminal Record")
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    scrollable_frame = ctk.CTkScrollableFrame(main_frame)
    scrollable_frame.pack(fill="both", expand=True)

    # --- Personal Information ---
    personal_frame = ctk.CTkFrame(scrollable_frame)
    personal_frame.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(personal_frame, text="Personal Information", font=("Roboto", 16, "bold")).pack(pady=5)
    ctk.CTkLabel(personal_frame, text="Full Name:").pack(anchor="w", padx=10)
    name_entry = ctk.CTkEntry(personal_frame)
    name_entry.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(personal_frame, text="Date of Birth (YYYY-MM-DD):").pack(anchor="w", padx=10)
    dob_entry = ctk.CTkEntry(personal_frame)
    dob_entry.pack(fill="x", padx=10, pady=5)

    # --- Physical Description ---
    physical_frame = ctk.CTkFrame(scrollable_frame)
    physical_frame.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(physical_frame, text="Physical Description", font=("Roboto", 16, "bold")).pack(pady=5)
    ctk.CTkLabel(physical_frame, text="Height (cm):").pack(anchor="w", padx=10)
    height_entry = ctk.CTkEntry(physical_frame)
    height_entry.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(physical_frame, text="Weight (kg):").pack(anchor="w", padx=10)
    weight_entry = ctk.CTkEntry(physical_frame)
    weight_entry.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(physical_frame, text="Eye Color:").pack(anchor="w", padx=10)
    eye_color_entry = ctk.CTkEntry(physical_frame)
    eye_color_entry.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(physical_frame, text="Hair Color:").pack(anchor="w", padx=10)
    hair_color_entry = ctk.CTkEntry(physical_frame)
    hair_color_entry.pack(fill="x", padx=10, pady=5)

    # --- Criminal Information ---
    criminal_frame = ctk.CTkFrame(scrollable_frame)
    criminal_frame.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(criminal_frame, text="Criminal Information", font=("Roboto", 16, "bold")).pack(pady=5)
    ctk.CTkLabel(criminal_frame, text="Crimes (comma separated):").pack(anchor="w", padx=10)
    crimes_entry = ctk.CTkEntry(criminal_frame)
    crimes_entry.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(criminal_frame, text="Status:").pack(anchor="w", padx=10)
    status_entry = ctk.CTkEntry(criminal_frame)
    status_entry.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(criminal_frame, text="Last Known Location:").pack(anchor="w", padx=10)
    location_entry = ctk.CTkEntry(criminal_frame)
    location_entry.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(criminal_frame, text="Additional Notes:").pack(anchor="w", padx=10)
    notes_entry = ctk.CTkTextbox(criminal_frame, height=100)
    notes_entry.pack(fill="x", padx=10, pady=5)

    # --- Image Uploads and Buttons ---
    button_frame = ctk.CTkFrame(scrollable_frame)
    button_frame.pack(fill="x", padx=10, pady=10)
    face_image_path = [None]
    additional_images = []
    status_label = ctk.CTkLabel(scrollable_frame, text="")
    status_label.pack(fill="x", padx=10, pady=5)

    # Progress overlay
    progress_overlay = ctk.CTkFrame(root, fg_color=("#000000", "#000000"), corner_radius=10)
    progress_overlay.place(relx=0.5, rely=0.5, anchor="center")
    progress_overlay.lower()
    progress_label = ctk.CTkLabel(progress_overlay, text="Processing...", font=("Roboto", 16, "bold"))
    progress_label.pack(padx=20, pady=(20, 10))
    progress_bar = ctk.CTkProgressBar(progress_overlay, orientation="horizontal", mode="indeterminate", width=250)
    progress_bar.pack(padx=20, pady=(0, 20))
    progress_bar.configure(progress_color="#4283BD")

    def show_progress(message="Processing...", color="#4283BD", determinate=False):
        progress_label.configure(text=message)
        progress_bar.configure(progress_color=color)
        progress_overlay.lift()
        progress_overlay.place(relx=0.5, rely=0.5, anchor="center")
        if determinate:
            progress_bar.configure(mode="determinate")
            progress_bar.set(1.0)
        else:
            progress_bar.configure(mode="indeterminate")
            progress_bar.start()
        root.update_idletasks()

    def hide_progress(delay=0):
        def _hide():
            progress_bar.stop()
            progress_overlay.lower()
            progress_overlay.place_forget()
        if delay > 0:
            root.after(delay, _hide)
        else:
            _hide()

    def upload_face_image():
        filetypes = (("Image files", "*.png;*.jpg;*.jpeg"), ("All files", "*.*"))
        filename = filedialog.askopenfilename(title="Upload Face Image", filetypes=filetypes)
        if filename:
            face_image_path[0] = filename
            status_label.configure(text=f"Face image selected: {os.path.basename(filename)}")

    def upload_additional_images():
        filetypes = (("Image files", "*.png;*.jpg;*.jpeg"), ("All files", "*.*"))
        filenames = filedialog.askopenfilenames(title="Upload Additional Images", filetypes=filetypes)
        if filenames:
            additional_images.clear()
            additional_images.extend(filenames)
            status_label.configure(text=f"{len(filenames)} additional images selected.")

    def set_form_state(state):
        widgets = [name_entry, dob_entry, height_entry, weight_entry, eye_color_entry, hair_color_entry, crimes_entry, status_entry, location_entry, notes_entry]
        for widget in widgets:
            widget.configure(state=state)

    def clear_form():
        name_entry.delete(0, "end")
        dob_entry.delete(0, "end")
        height_entry.delete(0, "end")
        weight_entry.delete(0, "end")
        eye_color_entry.delete(0, "end")
        hair_color_entry.delete(0, "end")
        crimes_entry.delete(0, "end")
        status_entry.delete(0, "end")
        location_entry.delete(0, "end")
        notes_entry.delete("1.0", "end")
        face_image_path[0] = None
        additional_images.clear()

    def submit_record():
        status_label.configure(text="Processing face encodings...")
        set_form_state("disabled")
        show_progress("Encoding face(s)...", color="#4283BD")
        all_image_paths = [face_image_path[0]] if face_image_path[0] else []
        all_image_paths += additional_images
        def background_work():
            import face_recognition
            import numpy as np
            import os
            import base64
            from PIL import Image as PILImage
            results = []
            for path in all_image_paths:
                try:
                    image = face_recognition.load_image_file(path)
                    pil_img = PILImage.fromarray(image)
                    pil_img.thumbnail((600, 600), PILImage.LANCZOS)
                    image = np.array(pil_img)
                    face_locations = face_recognition.face_locations(image, model='cnn')
                    if len(face_locations) == 0:
                        PILImage.fromarray(image).save(f"debug_no_face_{os.path.basename(path)}.jpg")
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
                root.after(0, lambda: [
                    status_label.configure(text="Face encoding error!"),
                    set_form_state("normal"),
                    show_progress(f"Error: {'; '.join(errors)}", color="#C0392B", determinate=True),
                    hide_progress(delay=1800)
                ])
                return
            try:
                root.after(0, lambda: show_progress("Uploading to database and images...", color="#4283BD"))
                data = {
                    'name': name_entry.get(),
                    'dob': dob_entry.get(),
                    'height': height_entry.get(),
                    'weight': weight_entry.get(),
                    'eye_color': eye_color_entry.get(),
                    'hair_color': hair_color_entry.get(),
                    'crimes': crimes_entry.get(),
                    'last_known_location': location_entry.get(),
                    'status': status_entry.get(),
                    'notes': notes_entry.get("1.0", "end-1c")
                }
                try:
                    from supabase_config import add_criminal_record, supabase
                    response = add_criminal_record(data)
                except Exception as e:
                    root.after(0, lambda e=e: [
                        status_label.configure(text="Failed to add criminal record."),
                        set_form_state("normal"),
                        show_progress(f"Error: {str(e)}", color="#C0392B", determinate=True),
                        hide_progress(delay=1800)
                    ])
                    return
                if response and response.data:
                    criminal_id = response.data[0]['id']
                    for encoding, path in encodings:
                        encoding_bytes = np.array(encoding, dtype=np.float64).tobytes()
                        b64 = base64.b64encode(encoding_bytes).decode('utf-8')
                        supabase.table('face_encodings').insert({
                            'criminal_id': criminal_id,
                            'encoding': str(b64),
                            'source_image': os.path.basename(path)
                        }).execute()
                    # Upload and add face image (main)
                    try:
                        if face_image_path[0]:
                            with open(face_image_path[0], 'rb') as f:
                                image_data = f.read()
                            filename = f"{criminal_id}_face{os.path.splitext(face_image_path[0])[1]}"
                            supabase.storage.from_('criminal-images').upload(
                                filename, 
                                image_data
                            )
                            image_url = supabase.storage.from_('criminal-images').get_public_url(filename)
                            supabase.table('criminal_images').insert({
                                'criminal_id': criminal_id,
                                'image_url': image_url,
                                'image_type': 'face'
                            }).execute()
                    except Exception as e:
                        root.after(0, lambda: show_progress(f"Warning: Failed to upload face image", color="#F39C12", determinate=True))
                    # Upload and add additional images
                    for image_path in additional_images:
                        try:
                            with open(image_path, 'rb') as f:
                                image_data = f.read()
                            filename = f"{criminal_id}_additional_{os.path.basename(image_path)}"
                            supabase.storage.from_('criminal-images').upload(
                                filename, 
                                image_data
                            )
                            image_url = supabase.storage.from_('criminal-images').get_public_url(filename)
                            supabase.table('criminal_images').insert({
                                'criminal_id': criminal_id,
                                'image_url': image_url,
                                'image_type': 'additional'
                            }).execute()
                        except Exception as e:
                            root.after(0, lambda path=image_path: show_progress(f"Warning: Failed to upload additional image: {path}", color="#F39C12", determinate=True))
                    root.after(0, lambda: [
                        status_label.configure(text="Record added successfully!"),
                        set_form_state("normal"),
                        show_progress("Success! Record added.", color="#27AE60", determinate=True),
                        clear_form(),
                        hide_progress(delay=1800)
                    ])
                else:
                    root.after(0, lambda: [
                        status_label.configure(text="Failed to add record."),
                        set_form_state("normal"),
                        show_progress("Error: Failed to add criminal record!", color="#C0392B", determinate=True),
                        hide_progress(delay=1800)
                    ])
            except Exception as e:
                root.after(0, lambda e=e: [
                    status_label.configure(text="An error occurred."),
                    set_form_state("normal"),
                    show_progress(f"Error: {str(e)}", color="#C0392B", determinate=True),
                    hide_progress(delay=1800)
                ])
        import threading
        threading.Thread(target=background_work, daemon=True).start()

    face_image_btn = ctk.CTkButton(button_frame, text="Upload Face Image", command=upload_face_image)
    face_image_btn.pack(side="left", padx=5, pady=5)
    additional_images_btn = ctk.CTkButton(button_frame, text="Upload Additional Images", command=upload_additional_images)
    additional_images_btn.pack(side="left", padx=5, pady=5)
    submit_btn = ctk.CTkButton(button_frame, text="Submit Record", command=submit_record)
    submit_btn.pack(side="right", padx=5, pady=5)

# Start with the welcome screen
show_welcome_screen()

root.mainloop()
