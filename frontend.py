import customtkinter as ctk
import tkinter.messagebox as tkmb

def login():
    username = "artabmaji"
    password = "123456"
    
    if user_entry.get() == username and user_pass.get() == password:
        show_welcome_screen()
    elif user_entry.get() == username and user_pass.get() != password:
        tkmb.showwarning(title='Wrong password', message='Please check your password')
    elif user_entry.get() != username and user_pass.get() == password:
        tkmb.showwarning(title='Wrong username', message='Please check your username')
    else:
        tkmb.showerror(title="Login Failed", message="Invalid Username and password")

def show_welcome_screen():
    # Clear the current contents of the window
    for widget in frame.winfo_children():
        widget.destroy()
    
    # Update the window title
    root.title("Welcome")
    
    # Add new content to the frame
    welcome_label = ctk.CTkLabel(frame, text="Moving forward!!", font=("Roboto", 24))
    welcome_label.pack(pady=20)
    
    # You can add more widgets here as needed
    
    # Optionally, you can add a logout button
    logout_button = ctk.CTkButton(frame, text="Logout", command=show_login_screen)
    logout_button.pack(pady=12, padx=10)

def show_login_screen():
    # Clear the current contents of the window
    for widget in frame.winfo_children():
        widget.destroy()
    
    # Update the window title
    root.title("Login System")
    
    # Recreate the login screen
    label = ctk.CTkLabel(master=frame, text="Login System", font=("Roboto", 24))
    label.pack(pady=20, padx=10)

    global user_entry, user_pass  # Make these global so they can be accessed in the login function
    user_entry = ctk.CTkEntry(master=frame, placeholder_text="Username")
    user_entry.pack(pady=12, padx=10)

    user_pass = ctk.CTkEntry(master=frame, placeholder_text="Password", show="*")
    user_pass.pack(pady=12, padx=10)

    button = ctk.CTkButton(master=frame, text="Login", command=login)
    button.pack(pady=12, padx=10)

    checkbox = ctk.CTkCheckBox(master=frame, text="Remember Me")
    checkbox.pack(pady=12, padx=10)

# Your existing code to set up the initial window and frame
root = ctk.CTk()
root.geometry("500x350")
root.title("Login System")

frame = ctk.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

# Show the login screen initially
show_login_screen()

root.mainloop()
