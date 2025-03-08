import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import tkinter.messagebox as tkmb
import os
from PIL import Image, ImageTk
import math
from datetime import datetime
import cv2

# Initialize global variables
middle_frame_right = None
sketch_canvas = None

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
        
        # Convert to CTkImage while preserving transparency
        self.image = ctk.CTkImage(image, size=(image.width, image.height))
        
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

    global user_entry, user_pass
    user_entry = ctk.CTkEntry(master=frame, placeholder_text="Username")
    user_entry.pack(pady=12, padx=10)

    user_pass = ctk.CTkEntry(master=frame, placeholder_text="Password", show="*")
    user_pass.pack(pady=12, padx=10)

    button = ctk.CTkButton(master=frame, text="Login", command=show_premain_screen)
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
    
    # Recreate the login screen
    label = ctk.CTkLabel(master=frame, text="Sign Up to Investigate", font=("Roboto", 24))
    label.pack(pady=20, padx=10)

    global user_entry, user_pass
    username_label = ctk.CTkLabel(master=frame, text="Enter username", font=("Roboto", 14))
    username_label.pack(pady=5, padx=10)
    user_entry = ctk.CTkEntry(master=frame, placeholder_text="Username")
    user_entry.pack(pady=12, padx=10)

    email_entry = ctk.CTkEntry(master=frame, placeholder_text="example@email.com")
    email_entry.pack(pady=12, padx=10)

    user_pass = ctk.CTkEntry(master=frame, placeholder_text="Password", show="*")
    user_pass.pack(pady=12, padx=10)

    pass_confirm = ctk.CTkEntry(master=frame, placeholder_text="Re-enter Password", show="*")
    pass_confirm.pack(pady=12, padx=10)

    button = ctk.CTkButton(master=frame, text="Sign Up", command=show_login_screen)
    button.pack(pady=12, padx=10)

def login():
    username = "artabmaji"
    password = "123456"
    
    if user_entry.get() == username and user_pass.get() == password:
        show_main_screen()
    elif user_entry.get() == username and user_pass.get() != password:
        tkmb.showwarning(title='Wrong password', message='Please check your password')
    elif user_entry.get() != username and user_pass.get() == password:
        tkmb.showwarning(title='Wrong username', message='Please check your username')
    else:
        tkmb.showerror(title="Login Failed", message="Invalid Username and password")


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
    
    button = ctk.CTkButton(master=frame, text="Create Sketch", command=show_main_screen)
    button.pack(pady=12, padx=10)
    
    upload_button = ctk.CTkButton(master=frame, text="Upload Sketch", command=show_premain_screen_2)
    upload_button.pack(pady=12, padx=10)


def show_premain_screen_2():
    global left_frame, upload_button1
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
    back_button.pack(anchor="nw", padx=10, pady=10)

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

    upload_button4 = ctk.CTkButton(master=button_frame, text="Logout", command=show_premain_screen)
    upload_button4.grid(row=0, column=3, padx=70)

    # Configure button_frame columns to distribute space evenly
    button_frame.grid_columnconfigure((0,1,2,3), weight=1)

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
    btn_frame = ctk.CTkFrame(left_frame)
    btn_frame.pack(fill="x", pady=10)

    # "Take Picture" button
    take_picture_btn = ctk.CTkButton(btn_frame, text="Take Picture", command=take_picture)
    take_picture_btn.pack(side="left", padx=5)

    # "Close Camera" button
    close_camera_btn = ctk.CTkButton(btn_frame, text="Close Camera", command=close_camera)
    close_camera_btn.pack(side="right", padx=5)


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
    global cap, left_label, upload_button1, take_picture_btn, btn_frame

    if cap:
        cap.release()

    # Clear everything inside left_frame (including buttons)
    for widget in left_frame.winfo_children():
        widget.destroy()

    # Re-enable "Capture Image" button
    upload_button1.configure(state="normal")



def upload_sketch():
    """Handle sketch upload from file system"""
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
            
            # Calculate size to fit in left_frame while maintaining aspect ratio
            frame_width = left_frame.winfo_width()
            frame_height = left_frame.winfo_height()
            
            # If frame dimensions are not yet available, use reasonable defaults
            if frame_width <= 1 or frame_height <= 1:
                frame_width = 300
                frame_height = 400
            
            # Calculate scaling factor to fit image in frame
            img_ratio = img.width / img.height
            frame_ratio = frame_width / frame_height
            
            if img_ratio > frame_ratio:
                new_width = frame_width
                new_height = int(frame_width / img_ratio)
            else:
                new_height = frame_height
                new_width = int(frame_height * img_ratio)
            
            # Resize image
            img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Create label and display image
            img_label = ctk.CTkLabel(left_frame, image=photo, text="")
            img_label.image = photo  # Keep a reference
            img_label.pack(expand=True)
            
            # Process the image for the canvas
            process_image(filename)
            tkmb.showinfo("Success", "Sketch uploaded successfully!")
        except Exception as e:
            tkmb.showerror("Error", f"Failed to upload sketch: {str(e)}")

def submit_image():
    """Handle image submission for processing"""
    # Check if there's an active image to submit
    if not hasattr(sketch_canvas, 'current_image'):
        tkmb.showwarning("Warning", "No image to submit. Please capture or upload an image first.")
        return
        
    try:
        # Save the current state of the canvas
        current_image = sketch_canvas.current_image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_filename = f"submitted_image_{timestamp}.png"
        current_image.save(save_filename)
        
        # Here you would add code to:
        # 1. Process the image for face detection
        faces, image = detect_faces(save_filename)
        
        # 2. Show results
        if len(faces) > 0:
            tkmb.showinfo("Success", f"Found {len(faces)} faces in the image.\nImage saved as {save_filename}")
        else:
            tkmb.showinfo("Result", "No faces detected in the image.")
            
    except Exception as e:
        tkmb.showerror("Error", f"Failed to process image: {str(e)}")

def process_image(image_path):
    """Common function to process images from either capture or upload"""
    try:
        # Load and display the image on the canvas
        image = Image.open(image_path)
        sketch_canvas.clear_canvas()
        sketch_canvas.current_image = image
        feature = sketch_canvas.add_feature(image_path)
        feature.bring_to_front()
        
    except Exception as e:
        tkmb.showerror("Error", f"Failed to process image: {str(e)}")

    upload_button4 = ctk.CTkButton(master=button_frame, text="Logout", command=show_premain_screen)
    upload_button4.grid(row=0, column=3, padx=70)

    # Configure button_frame columns to distribute space evenly
    button_frame.grid_columnconfigure((0,1,2,3), weight=1)

   
    


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
    
    def submit_sketch():
        print("Sketch submitted")
    
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

# Start with the welcome screen
show_welcome_screen()

root.mainloop()