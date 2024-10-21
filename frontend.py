import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as tkmb
import os
from PIL import Image, ImageTk


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
    bg_image = Image.open("images/Detective_007.jpg")  # Adjust the path as needed
    bg_photo = ctk.CTkImage(bg_image, size=(1200, 700))  # Adjust size as needed

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
    # back_button = ctk.CTkButton(frame, text="←", command=show_welcome_screen, width=50, fg_color="transparent", hover_color="#EBEBEB")
    back_button = ctk.CTkButton(frame, text="←", command=show_welcome_screen, width=50,
                            fg_color="transparent",  # Default button color
                            text_color="white",    # Default text color
                            hover_color="#4283BD", # Light blue color on hover
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
    # Placeholder for signup screen
    tkmb.showinfo("Sign Up", "Sign Up functionality not implemented yet.")

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


def clear_right_frame():
    for widget in right_frame.winfo_children():
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
    main_frame.grid_rowconfigure(0, weight=1)  # Allow row expansion
    
    # Adjust the weights for each column to control how much space they take
    main_frame.grid_columnconfigure(0, weight=0)  # Left column (dashboard)
    main_frame.grid_columnconfigure(1, weight=10)  # Middle column (larger area)
    main_frame.grid_columnconfigure(2, weight=3)  # Right column
    
    # Left column (dashboard)
    left_frame = ctk.CTkFrame(main_frame)
    left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    left_frame.grid_rowconfigure(0, weight=1) # Allow vertical expansion

    
    # Right column
    global right_frame
    right_frame = ctk.CTkFrame(main_frame)
    right_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    # Image display area in the right column
    image_label = ctk.CTkLabel(right_frame, text="Select a facial element", width=200, height=200)
    image_label.pack(pady=20)
    
    # Add facial element buttons to left_frame
    facial_elements = ["Head", "Hair", "Nose", "Eye", "Eyebrows", "Lips", "Moustache", "Ears"]
    for element in facial_elements:
        button = ctk.CTkButton(left_frame, text=element, 
                               command=lambda e=element: show_facial_element(e),
                               fg_color="#016764", hover_color="#014848")
        button.pack(anchor="n", padx=5, pady=5)

    
    # Function to display the selected facial element image
    def show_facial_element(element):
        element_folder = element.lower()
        if element_folder == "moustache":
            element_folder = "mustach"  # Adjust for the spelling in the folder name
        image_folder = os.path.join("face_features", element_folder)
        print(f"Searching for images in: {image_folder}")
        
        if os.path.exists(image_folder) and os.path.isdir(image_folder):
            image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            if image_files:
                display_image_matrix(image_files, image_folder, element)
            else:
                print(f"No image files found in {image_folder}")
                clear_right_frame()
                ctk.CTkLabel(right_frame, text=f"No images for {element}").pack(pady=20)
        else:
            print(f"Folder not found: {image_folder}")
            clear_right_frame()
            ctk.CTkLabel(right_frame, text=f"No folder for {element}").pack(pady=20)

    def display_image_matrix(image_files, image_folder, element):
        clear_right_frame()
        
        # Create a scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(right_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create a grid layout
        row = 0
        col = 0
        for file in image_files:
            image_path = os.path.join(image_folder, file)
            img = Image.open(image_path)
            img = img.resize((150, 150), Image.LANCZOS)
            photo = ctk.CTkImage(img, size=(150, 150))
            
            image_button = ctk.CTkButton(scrollable_frame, image=photo, text="", width=150, height=150)
            image_button.grid(row=row, column=col, padx=5, pady=5)
            
            col += 1
            if col == 2:  # Move to next row after 2 columns
                col = 0
                row += 1
    
    # Add label to show selected element
    ctk.CTkLabel(right_frame, text=f"Selected: {element}").pack(pady=10)



    # Middle column
    middle_frame = ctk.CTkFrame(main_frame)
    middle_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    
    # No explicit width or height for middle_frame; rely on grid configuration
    
    
    # No explicit width or height for right_frame; rely on grid configuration
    logout_button = ctk.CTkButton(right_frame, text="Logout", command=show_welcome_screen, fg_color="#FF0000", hover_color="#9D0B28")
    logout_button.pack(anchor="n", padx=10, pady=10)
    
    def clear_canvas():
    # Add code here to clear the canvas
        print("Canvas cleared")  # Placeholder action

    def submit_sketch():
    # Add code here to submit the sketch
        print("Sketch submitted")  # Placeholder action
    
    clear_canvas_button = ctk.CTkButton(right_frame, text="Clear Canvas", command=clear_canvas, fg_color="#56666F", hover_color="#314048")
    clear_canvas_button.pack(anchor="s", pady=5)
    
    submit_sketch_button = ctk.CTkButton(right_frame, text="Submit Sketch", command=submit_sketch, fg_color="#522377", hover_color="#36195B")
    submit_sketch_button.pack(anchor="s", pady=5)



# Start with the welcome screen
show_welcome_screen()

root.mainloop()
