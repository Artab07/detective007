import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as tkmb
import os
from PIL import Image, ImageTk

# Initialize global variables
middle_frame_right = None

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.geometry("1200x700")
root.title("Detective 007")

def show_welcome_screen():
    # Update the window title first
    root.title("Detective 007")
    
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
    global right_frame, middle_frame, middle_frame_right
    right_frame = ctk.CTkFrame(main_frame)
    right_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
    
    # Middle column
    middle_frame = ctk.CTkFrame(main_frame)
    middle_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # Divide right frame into 3 parts
    # 1. Top part for logout button
    top_frame = ctk.CTkFrame(right_frame)
    top_frame.pack(side="top", fill="x", padx=5, pady=5)
    
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

    def clear_canvas():
        print("Canvas cleared")

    def submit_sketch():
        print("Sketch submitted")
    
    clear_btn = ctk.CTkButton(bottom_frame, text="Clear Canvas", command=clear_canvas, 
                             fg_color="#56666F", hover_color="#314048")
    clear_btn.pack(side="left", padx=5, pady=5)
    
    submit_btn = ctk.CTkButton(bottom_frame, text="Submit Sketch", command=submit_sketch, 
                              fg_color="#522377", hover_color="#36195B")
    submit_btn.pack(side="right", padx=5, pady=5)
    
    # Add facial element buttons to left_frame
    facial_elements = ["Head", "Hair", "Nose", "Eye", "Eyebrows", "Lips", "Moustache", "Ears"]
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
    global middle_frame_right
    clear_middle_frame_right()
    
    # Create a scrollable frame
    scrollable_frame = ctk.CTkScrollableFrame(middle_frame_right)
    scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create a grid layout
    row = 0
    col = 0
    max_cols = 2  # Number of columns in the grid
    image_size = (150, 150)
    
    # First, add the label showing the selected element
    label = ctk.CTkLabel(scrollable_frame, text=f"Selected: {element}")
    label.grid(row=row, column=0, columnspan=max_cols, pady=10)
    row += 1  # Move to next row
    
    # Then add the images
    for file in image_files:
        image_path = os.path.join(image_folder, file)
        # Open the original image
        img = Image.open(image_path)
        
        # Convert the image to RGBA if it isn't already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create a white background image
        background = Image.new('RGBA', img.size, (255, 255, 255, 255))
        
        # Paste the image on the white background using the alpha channel as mask
        composite = Image.alpha_composite(background, img)
        
        # Convert back to RGB mode (removing alpha channel)
        composite = composite.convert('RGB')
        
        # Resize the image
        composite = composite.resize(image_size, Image.LANCZOS)
        
        # Create CTkImage
        photo = ctk.CTkImage(composite, size=image_size)
        
        # Create a frame with white background for the image
        image_frame = ctk.CTkFrame(scrollable_frame, fg_color="white")
        image_frame.grid(row=row, column=col, padx=5, pady=5)
        
        # Create the button with the image inside the white frame
        image_button = ctk.CTkButton(image_frame, 
                                   image=photo, 
                                   text="", 
                                   width=image_size[0], 
                                   height=image_size[1],
                                   fg_color="white",  # Button background color
                                   hover_color="#4283BD")  # Light gray on hover
        image_button.pack(padx=2, pady=2)
        
        col += 1
        if col == max_cols:  # Move to next row after max_cols columns
            col = 0
            row += 1

    # Configure grid columns to be equal width
    for i in range(max_cols):
        scrollable_frame.grid_columnconfigure(i, weight=1)

# Start with the welcome screen
show_welcome_screen()

root.mainloop()