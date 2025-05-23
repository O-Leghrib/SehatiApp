import tkinter as tk
from tkinter import messagebox
from tkinter import Entry, Label, Frame
from PIL import Image, ImageTk
import bcrypt
import sqlite3
import os
import customtkinter as ctk

class SignUpPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="white")

        # Ensure the database and table exist when the page is initialized
        self._initialize_database()
        self.setup_ui()

    def _initialize_database(self):
        """
        Connects to the SQLite database and creates the 'users' table
        if it doesn't already exist. This table will store basic
        user credentials.
        """
        conn = None # Initialize conn to None
        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
            """)
            conn.commit()
        except sqlite3.Error as e:
            # Handle potential errors during database initialization,
            # e.g., by logging them or showing an error to the user.
            print(f"Database initialization error: {e}")
            messagebox.showerror("Database Error", f"Could not initialize the database: {e}", parent=self.controller) # Added parent
        finally:
            if conn:
                conn.close()

    def setup_ui(self):
        # Ensure the 'images' directory exists
        if not os.path.exists("images"):
            os.makedirs("images")
            # You might want to inform the user or handle this more gracefully
            print("INFO: 'images' directory created. Please add 'sign.png', 'transparent.png', and 'eye.png' to it.")

        # Attempt to load images, with fallbacks or error handling
        try:
            self.image_path = os.path.join("images", "sign.png")
            self.original_image = Image.open(self.image_path)
        except FileNotFoundError:
            print(f"Error: sign.png not found in images folder. Using a placeholder.")
            # Create a placeholder image if main one is missing
            self.original_image = Image.new('RGB', (800, 600), color = 'lightblue')
            # Optionally, add text to the placeholder
            # from PIL import ImageDraw
            # draw = ImageDraw.Draw(self.original_image)
            # draw.text((10,10), "Sign Up Image Placeholder", fill=(0,0,0))


        self.bg_image = ImageTk.PhotoImage(self.original_image)

        self.bg_label = Label(self, image=self.bg_image, bg="white") # Ensure bg matches
        self.bg_label.image = self.bg_image # Keep a reference
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.bind("<Configure>", self.resize_image)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.frame = Frame(self, bg="white")
        # Changed placement to be on the right side, dynamic, with a margin
        # relx=1.0 positions the anchor point at the far right of the parent.
        # anchor='e' means the anchor point on this frame is its east (right-center) edge.
        # x=-50 provides a 50-pixel margin from the right edge.
        # rely=0.5 keeps it vertically centered.
        self.frame.place(relx=1.0, rely=0.5, x=-50, anchor='e', width=500, height=750)

        title = Label(self.frame, text="Create your account", font=("Georgia", 30), fg='#48bfe3', bg='white') # Slightly smaller font
        title.pack(pady=(40, 30)) # Adjusted padding

        self.entry_username = self.create_labeled_entry(self.frame, "Username")
        self.entry_email = self.create_labeled_entry(self.frame, "Email")
        self.entry_password = self.create_password_entry(self.frame, "Password")
        self.entry_confirm = self.create_password_entry(self.frame, "Confirm Password")

        self.signup_btn = ctk.CTkButton(self.frame,
                                        width=280,
                                        height=40,
                                        text="Sign Up",
                                        font=("Times New Roman", 19, "bold"),
                                        text_color="white",
                                        fg_color="#48bfe3",
                                        hover_color="#3CA0C5", # Slightly different hover
                                        command=self.validate_signup) # Changed command
        self.signup_btn.pack(pady=(20, 10), ipady=4) # Adjusted padding

        self.back_btn = ctk.CTkButton(self.frame,
                                      text="Back to Login",
                                      width=280,
                                      height=40,
                                      font=("Times New Roman", 19, "bold"),
                                      text_color="white",
                                      fg_color="#48bfe3",
                                      hover_color="#3CA0C5",
                                      command=lambda: self.controller.show_frame("LogSign"))
        self.back_btn.pack(pady=(10, 20), ipady=4) # Adjusted padding

    def resize_image(self, event):
        if not hasattr(self, 'original_image'): return # Guard against missing image

        new_width = event.width
        new_height = event.height
        
        # Prevent resizing to zero dimensions which causes errors
        if new_width <= 0 or new_height <= 0:
            return

        try:
            resized_image = self.original_image.resize((new_width, new_height), Image.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(resized_image)
            self.bg_label.configure(image=self.bg_image)
            self.bg_label.image = self.bg_image # Update reference
        except Exception as e:
            print(f"Error resizing image: {e}")


    def create_labeled_entry(self, parent, label_text):
        label = Label(parent, text=label_text, fg='#48bfe3', bg='white', font=("Arial", 14, "bold")) # Slightly smaller font
        label.pack(anchor="n", pady=(5,2)) # Added small padding

        container = Frame(parent, bg="white")
        container.pack(pady=(2, 10), anchor="center")

        entry = Entry(container, width=25, bg="white", fg='#48bfe3', # Increased width
                      insertbackground='#48bfe3', highlightthickness=1,
                      highlightbackground='#48bfe3', highlightcolor='#48bfe3', # Added highlightcolor
                      borderwidth=1, relief="solid", # Changed relief
                      font=("Times New Roman", 14, "bold")) # Slightly smaller font
        entry.pack(side="left", ipady=5, padx=(0,5)) # Added padding to separate from icon

        # Transparent icon for alignment (if needed)
        try:
            icon_path = os.path.join("images", "transparent.png")
            icon_img = Image.open(icon_path).resize((20, 20), Image.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_img)
        except FileNotFoundError:
            # Create a small transparent placeholder if image is missing
            icon_img = Image.new('RGBA', (20, 20), (0,0,0,0))
            icon_photo = ImageTk.PhotoImage(icon_img)
            print(f"Warning: transparent.png not found. Using placeholder.")


        icon_label = Label(container, image=icon_photo, bg="white")
        icon_label.image = icon_photo # Keep a reference
        icon_label.pack(side="left", padx=(0, 0))

        return entry

    def create_password_entry(self, parent, label_text="Password"):
        label = Label(parent, text=label_text, fg='#48bfe3', bg='white', font=("Arial", 14, "bold")) # Slightly smaller font
        label.pack(anchor="n", pady=(5,2)) # Added small padding

        container = Frame(parent, bg="white")
        container.pack(pady=(2, 10))

        entry = Entry(container, width=25, bg="white", fg='#48bfe3', # Increased width
                      insertbackground='#48bfe3', highlightthickness=1,
                      highlightbackground='#48bfe3', highlightcolor='#48bfe3', # Added highlightcolor
                      borderwidth=1, relief="solid", show="*", # Changed relief
                      font=("Times New Roman", 14, "bold")) # Slightly smaller font
        entry.pack(side="left", ipady=5)

        try:
            eye_path = os.path.join("images", "eye.png")
            eye_img = Image.open(eye_path).resize((20, 20), Image.LANCZOS)
            eye_photo = ImageTk.PhotoImage(eye_img)
        except FileNotFoundError:
            # Create a placeholder if eye.png is missing
            eye_img = Image.new('RGB', (20,20), 'gray') # Simple placeholder
            # from PIL import ImageDraw
            # draw = ImageDraw.Draw(eye_img)
            # draw.text((2,2), "👁", fill='black') # Placeholder text
            eye_photo = ImageTk.PhotoImage(eye_img)
            print(f"Warning: eye.png not found. Using placeholder.")


        eye_label = Label(container, image=eye_photo, bg="white", cursor="hand2") # Changed cursor
        eye_label.image = eye_photo # Keep a reference
        eye_label.pack(side="left", padx=(5, 0))
        eye_label.bind("<Button-1>", lambda e, entry_widget=entry: self.toggle_password(entry_widget, eye_label))

        return entry

    def toggle_password(self, entry_widget, eye_label):
        # Ideally, you'd change the eye icon too (e.g., eye-slash)
        if entry_widget.cget("show") == "*":
            entry_widget.config(show="")
            # eye_label.configure(image=self.eye_open_icon) # If you have an open eye icon
        else:
            entry_widget.config(show="*")
            # eye_label.configure(image=self.eye_closed_icon) # Back to closed eye icon

    def validate_signup(self):
        username = self.entry_username.get().strip()
        email = self.entry_email.get().strip()
        password = self.entry_password.get().strip()
        confirm = self.entry_confirm.get().strip()

        if not username or not email or not password or not confirm:
            messagebox.showerror("Error", "All fields are required!", parent=self)
            return

        # Basic email validation (can be more sophisticated)
        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "Please enter a valid email address.", parent=self)
            return

        if len(password) < 6: # Example: Minimum password length
            messagebox.showerror("Error", "Password must be at least 6 characters long.", parent=self)
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match!", parent=self)
            return

        success, message = self.signup_user(email, username, password) # Renamed for clarity
        if success:
            messagebox.showinfo("Success", message, parent=self)
            # Navigate to SihatiForm as per original button's implication for next steps
            self.controller.show_frame("SihatiForm")
            # Clear fields after successful signup
            self.entry_username.delete(0, tk.END)
            self.entry_email.delete(0, tk.END)
            self.entry_password.delete(0, tk.END)
            self.entry_confirm.delete(0, tk.END)
        else:
            messagebox.showerror("Error", message, parent=self)

    def signup_user(self, email, username, password):
        """
        Hashes the password and inserts the new user into the database.
        The 'users' table is assumed to be created by _initialize_database.
        """
        conn = None # Initialize conn to None
        try:
            # Encode password and hash it
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt)
        except Exception as e:
            print(f"Error hashing password: {e}")
            return False, "Error processing password."

        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            # The table should already exist due to _initialize_database
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                           (username, email, hashed_password))
            conn.commit()
            return True, "Account created successfully! Please proceed to the next step."
        except sqlite3.IntegrityError as e:
            # This error occurs if username or email already exists (due to UNIQUE constraint)
            if "username" in str(e).lower():
                return False, "Username already exists. Please choose a different one."
            elif "email" in str(e).lower():
                return False, "Email address already registered. Please use a different one or login."
            else:
                print(f"Database IntegrityError: {e}")
                return False, "A user with this username or email may already exist."
        except sqlite3.Error as e:
            # Catch other potential SQLite errors
            print(f"Database error during signup: {e}")
            return False, f"Database error: {e}"
        finally:
            if conn:
                conn.close()