import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
from tkinter import messagebox
import customtkinter as ctk
import os

# Import the login_user function from your centralized db_operations file
from db_operations import login_user

class LogSign(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.master = parent

        self.configure(bg="white")

        # --- REMOVED: self.setup_database() ---
        # Database initialization is now handled globally in app.py via initialize_database_unified()

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        try:
            image_path = os.path.join("images", "login.png")
            if not os.path.exists(image_path):
                # Fallback if image not found (e.g., development environment)
                print(f"WARNING: '{image_path}' not found. Using a dummy image.")
                self.original_image = Image.new("RGB", (800, 600), "lightgray")
            else:
                self.original_image = Image.open(image_path)
        except Exception as e:
            print(f"ERROR: Could not load image at '{image_path}': {e}")
            self.original_image = Image.new("RGB", (800, 600), "lightgray") # Fallback if PIL errors

        self.bg_image = ImageTk.PhotoImage(self.original_image)
        self.bg_label = Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bind("<Configure>", self.resize_image)

        # Frame positioning for login elements
        self.border_x_ratio = 0.6  # Example: start at 60% of window width
        self.border_y_ratio = 0.05 # Example: start at 5% of window height
        self.border_width_ratio = 0.35 # Example: 35% of window width
        self.border_height_ratio = 0.9 # Example: 90% of window height (adjust as needed)

        self.frame = Frame(self, bg="white")
        # Place the frame using relative positioning for responsiveness
        self.frame.place(relx=self.border_x_ratio, rely=self.border_y_ratio, 
                         relwidth=self.border_width_ratio, relheight=self.border_height_ratio)


        self.top_label = Label(self.frame, text="Log in to Sehati", font=("Georgia", 42), fg='#48bfe3', bg='white')
        self.top_label.pack(pady=(50, 70))

        self.username_TEXT = self.create_labeled_entry(self.frame, "Username")
        self.password_TEXT = self.create_password_entry(self.frame)

        self.button_login = ctk.CTkButton(self.frame,
                                          width=240,
                                          height=40,
                                          text="Log in",
                                          font=("Times New Roman", 19, "bold"),
                                          text_color="white",
                                          fg_color="#48bfe3",
                                          hover_color="#48bfe3",
                                          command=self.validate_login)
        self.button_login.pack(pady=(25, 5), ipady=4)

        self.signup_label = ctk.CTkLabel(self.frame,
                                         text="Don't have an account?",
                                         text_color='#48bfe3',
                                         font=("Times New Roman", 19, "bold"),
                                         fg_color="transparent")
        self.signup_label.pack(pady=(25, 2)) # Adjusted pady to separate from login button

        self.button_signup = ctk.CTkButton(self.frame,
                                           width=240,
                                           height=40,
                                           text="Sign up",
                                           font=("Times New Roman", 19, "bold"),
                                           text_color="white",
                                           fg_color="#48bfe3",
                                           hover_color="#48bfe3",
                                           command=lambda:self.controller.show_frame("SignUpPage"))
        self.button_signup.pack(pady=(5, 5), ipady=4) # Adjusted pady for spacing

    # --- REMOVED: setup_database method ---
    # This is handled globally by initialize_database_unified() in app.py

    def resize_image(self, event):
        new_width = event.width
        new_height = event.height
        if new_width > 0 and new_height > 0 and hasattr(self, 'original_image'):
            resized_image = self.original_image.resize((new_width, new_height), Image.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(resized_image)
            self.bg_label.config(image=self.bg_image)
            self.bg_label.image = self.bg_image # Keep a reference!
            
            # Reposition the login frame based on new window size
            self.frame.place(relx=self.border_x_ratio, rely=self.border_y_ratio, 
                             relwidth=self.border_width_ratio, relheight=self.border_height_ratio)


    def create_labeled_entry(self, parent, label_text):
        label = Label(parent, text=label_text, fg='#48bfe3', bg='white', font=("Arial", 15, "bold"))
        label.pack(anchor="n")

        container = Frame(parent, bg="white")
        container.pack(pady=(2, 30))

        entry = Entry(container, width=20, bg="white", fg='#48bfe3', insertbackground='#48bfe3',
                      highlightthickness=1, highlightbackground='#48bfe3', borderwidth=1, relief="ridge",
                      font=("Times New Roman", 13, "bold"))
        entry.pack(side="left", ipady=5)

        # Dummy element for alignment, if necessary (you might remove it if not visually needed)
        dummy = Label(container, bg="white", width=2)
        dummy.pack(side="left", padx=(5, 0))

        return entry

    def create_password_entry(self, parent, label_text="Password"):
        label = Label(parent, text=label_text, fg='#48bfe3', bg='white',font=("Arial", 15, "bold"))
        label.pack(anchor="n")

        container = Frame(parent, bg="white")
        container.pack(pady=(2, 30))

        entry = Entry(container, width=20, bg="white", fg='#48bfe3', insertbackground='#48bfe3',
                      highlightthickness=1, highlightbackground='#48bfe3', borderwidth=1, relief="ridge",
                      show="*", font=("Times New Roman", 13, "bold"))
        entry.pack(side="left", ipady=5)

        try:
            eye_path = os.path.join("images", "eye.png")
            if not os.path.exists(eye_path):
                print(f"WARNING: '{eye_path}' not found. Using a default square for eye icon.")
                eye_img = Image.new("RGB", (20, 20), "blue")
            else:
                eye_img = Image.open(eye_path).resize((20, 20), Image.LANCZOS)
            self.eye_icon = ImageTk.PhotoImage(eye_img)
        except Exception as e:
            print(f"ERROR: Could not load eye image: {e}")
            eye_img = Image.new("RGB", (20, 20), "red") # Fallback in case of PIL errors
            self.eye_icon = ImageTk.PhotoImage(eye_img)

        eye_label = Label(container, image=self.eye_icon, bg="white", cursor="hand2") # Changed cursor
        eye_label.image = self.eye_icon # Keep a reference!
        eye_label.pack(side="left", padx=(5, 0))
        eye_label.bind("<Button-1>", lambda e, entry=entry: self.toggle_password(entry))

        return entry

    def toggle_password(self, entry_widget):
        if entry_widget.cget("show") == "*":
            entry_widget.config(show="")
        else:
            entry_widget.config(show="*")

    def validate_login(self):
        username = self.username_TEXT.get().strip()
        password = self.password_TEXT.get().strip()

        if not username or not password:
            messagebox.showerror("Login Error", "Please enter both username and password.")
            return

        # --- IMPORTANT CHANGE: Use login_user from db_operations ---
        user_id = login_user(username, password)
        # --- END IMPORTANT CHANGE ---

        if user_id is not None: # login_user returns user_id (int) or None
            messagebox.showinfo("Login Success", f"Welcome, {username}!")
            # --- IMPORTANT: Set the current user ID in the main app controller ---
            self.controller.set_current_user_id(user_id) 
            # --- Then navigate to the home page ---
            self.controller.show_frame("homepage")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    # --- REMOVED: open_signup_window method as button directly calls show_frame ---
    # The signup button now directly calls self.controller.show_frame("SignUpPage")