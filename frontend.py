import customtkinter as ctk
import tkinter.messagebox as tkmb

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.geometry("1200x700")
root.title("Detective 007")

def show_welcome_screen():
    # Clear the current contents of the window
    for widget in root.winfo_children():
        widget.destroy()
    
    frame = ctk.CTkFrame(master=root)
    frame.pack(pady=20, padx=60, fill="both", expand=True)

    welcome_label = ctk.CTkLabel(frame, text="Welcome, Agent.\nDetective 007 is on the case,\nand you're now part of the mission.", 
                                 font=("Roboto", 18), justify="center")
    welcome_label.pack(pady=20, padx=10)

    sign_in_button = ctk.CTkButton(frame, text="Sign In", command=show_login_screen)
    sign_in_button.pack(pady=12, padx=10)

    sign_up_button = ctk.CTkButton(frame, text="Sign Up", command=show_signup_screen)
    sign_up_button.pack(pady=12, padx=10)

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

def show_main_screen():
    # Clear the current contents of the window
    for widget in root.winfo_children():
        widget.destroy()
    
    # Update the window title
    root.title("Detective 007 - Main Screen")
    
    # Create main frame
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Create three columns
    main_frame.grid_columnconfigure(0, weight=1)  # Left column
    main_frame.grid_columnconfigure(1, weight=7)  # Middle column (70% of the frame)
    main_frame.grid_columnconfigure(2, weight=1)  # Right column

    # Left column (dashboard)
    left_frame = ctk.CTkFrame(main_frame)
    left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    dashboard_label = ctk.CTkLabel(left_frame, text="Dashboard", font=("Roboto", 18))
    dashboard_label.pack(pady=10)

    buttons = ["Button 1", "Button 2", "Button 3", "Button 4"]
    for button_text in buttons:
        button = ctk.CTkButton(left_frame, text=button_text)
        button.pack(pady=5)

    # Middle column (blank area)
    middle_frame = ctk.CTkFrame(main_frame)
    middle_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # Right column
    right_frame = ctk.CTkFrame(main_frame)
    right_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    # Logout button (top-right)
    logout_button = ctk.CTkButton(right_frame, text="Logout", command=show_welcome_screen)
    logout_button.pack(anchor="ne", padx=10, pady=10)

    # Create a frame for the bottom buttons
    bottom_buttons_frame = ctk.CTkFrame(right_frame)
    bottom_buttons_frame.pack(side="bottom", padx=10, pady=10)

    # Clear Canvas and Submit Sketch buttons (bottom-right)
    clear_canvas_button = ctk.CTkButton(bottom_buttons_frame, text="Clear Canvas")
    clear_canvas_button.pack(pady=5)

    submit_sketch_button = ctk.CTkButton(bottom_buttons_frame, text="Submit Sketch")
    submit_sketch_button.pack(pady=5)



# Start with the welcome screen
show_welcome_screen()

root.mainloop()
