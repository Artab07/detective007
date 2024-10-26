import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as tkmb
import os
from PIL import Image, ImageTk
import math

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
        
        # Bind mouse events
        self.canvas.tag_bind(self.id, '<Button-1>', self.on_press)
        self.canvas.tag_bind(self.id, '<B1-Motion>', self.on_drag)
        self.canvas.tag_bind(self.id, '<Button-3>', self.show_context_menu)
        
        # Create resize handles
        self.create_handles()

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
        
        # Convert to PhotoImage while preserving transparency
        self.image = ImageTk.PhotoImage(image)
        
        # Update or create canvas image
        if hasattr(self, 'id'):
            self.canvas.delete(self.id)
        self.id = self.canvas.create_image(
            self.position[0], self.position[1],
            image=self.image,
            anchor='center',
            tags='feature'
        )
        
        # Update handles
        if hasattr(self, 'handles'):
            self.update_handles()
    
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
        
        self.update_handles()
        self.hide_handles()
    
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
    
    def show_handles(self):
        for handle in self.handles:
            self.canvas.itemconfig(handle, state='normal')
    
    def hide_handles(self):
        for handle in self.handles:
            self.canvas.itemconfig(handle, state='hidden')
    
    def on_press(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.start_pos = self.position
        
        # Bring to front
        self.canvas.tag_raise(self.id)
        for handle in self.handles:
            self.canvas.tag_raise(handle)
        
        # Show handles
        self.show_handles()
    
    def on_drag(self, event):
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        self.position = (self.start_pos[0] + dx, self.start_pos[1] + dy)
        self.canvas.coords(self.id, self.position[0], self.position[1])
        self.update_handles()
    
    def start_resize(self, event, handle_pos):
        self.resize_start = (event.x, event.y)
        self.resize_start_scale = self.scale
        self.resize_handle = handle_pos
    
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
        
        # Update image
        self.update_image()
    
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
        self.canvas.tag_raise(self.id)
        for handle in self.handles:
            self.canvas.tag_raise(handle)
    
    def send_to_back(self):
        self.canvas.tag_lower(self.id)
    
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
    back_button = ctk.CTkButton(frame, text="←", command=show_welcome_screen, width=50,
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

    button = ctk.CTkButton(master=frame, text="Login", command=login)
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