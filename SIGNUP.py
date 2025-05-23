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

        # لا حاجة لاستدعاء _initialize_database هنا.
        # يجب أن تُستدعى initialize_database_unified() مرة واحدة عند بدء التطبيق الرئيسي.
        # self._initialize_database() # <--- تم إزالة هذا السطر
        self.setup_ui()

    # تم حذف _initialize_database() من هنا لأنها أصبحت دالة عامة (initialize_database_unified)

    def setup_ui(self):
        if not os.path.exists("images"):
            os.makedirs("images")
            print("INFO: 'images' directory created. Please add 'sign.png', 'transparent.png', and 'eye.png' to it.")

        try:
            self.image_path = os.path.join("images", "sign.png")
            self.original_image = Image.open(self.image_path)
        except FileNotFoundError:
            print(f"Error: sign.png not found in images folder. Using a placeholder.")
            self.original_image = Image.new('RGB', (800, 600), color = 'lightblue')

        self.bg_image = ImageTk.PhotoImage(self.original_image)
        self.bg_label = Label(self, image=self.bg_image, bg="white")
        self.bg_label.image = self.bg_image
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bind("<Configure>", self.resize_image)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.frame = Frame(self, bg="white")
        self.frame.place(relx=0.8, rely=0.6, anchor="center", width=400, height=700)

        title = Label(self.frame, text="Create your account", font=("Georgia", 30), fg='#48bfe3', bg='white')
        title.pack(pady=(40, 30))

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
                                        hover_color="#3CA0C5",
                                        command=self.validate_signup)
        self.signup_btn.pack(pady=(20, 10), ipady=4)

        self.back_btn = ctk.CTkButton(self.frame,
                                        text="Back to Login",
                                        width=280,
                                        height=40,
                                        font=("Times New Roman", 19, "bold"),
                                        text_color="white",
                                        fg_color="#48bfe3",
                                        hover_color="#3CA0C5",
                                        command=lambda: self.controller.show_frame("LogSign"))
        self.back_btn.pack(pady=(10, 20), ipady=4)

    def resize_image(self, event):
        if not hasattr(self, 'original_image'): return

        new_width = event.width
        new_height = event.height
        
        if new_width <= 0 or new_height <= 0:
            return

        try:
            resized_image = self.original_image.resize((new_width, new_height), Image.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(resized_image)
            self.bg_label.configure(image=self.bg_image)
            self.bg_label.image = self.bg_image
        except Exception as e:
            print(f"Error resizing image: {e}")

    def create_labeled_entry(self, parent, label_text):
        label = Label(parent, text=label_text, fg='#48bfe3', bg='white', font=("Arial", 14, "bold"))
        label.pack(anchor="n", pady=(5,2))

        container = Frame(parent, bg="white")
        container.pack(pady=(2, 10), anchor="center")

        entry = Entry(container, width=25, bg="white", fg='#48bfe3',
                        insertbackground='#48bfe3', highlightthickness=1,
                        highlightbackground='#48bfe3', highlightcolor='#48bfe3',
                        borderwidth=1, relief="solid",
                        font=("Times New Roman", 14, "bold"))
        entry.pack(side="left", ipady=5, padx=(0,5))

        try:
            icon_path = os.path.join("images", "transparent.png")
            icon_img = Image.open(icon_path).resize((20, 20), Image.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_img)
        except FileNotFoundError:
            icon_img = Image.new('RGBA', (20, 20), (0,0,0,0))
            icon_photo = ImageTk.PhotoImage(icon_img)
            print(f"Warning: transparent.png not found. Using placeholder.")

        icon_label = Label(container, image=icon_photo, bg="white")
        icon_label.image = icon_photo
        icon_label.pack(side="left", padx=(0, 0))

        return entry

    def create_password_entry(self, parent, label_text="Password"):
        label = Label(parent, text=label_text, fg='#48bfe3', bg='white', font=("Arial", 14, "bold"))
        label.pack(anchor="n", pady=(5,2))

        container = Frame(parent, bg="white")
        container.pack(pady=(2, 10))

        entry = Entry(container, width=25, bg="white", fg='#48bfe3',
                        insertbackground='#48bfe3', highlightthickness=1,
                        highlightbackground='#48bfe3', highlightcolor='#48bfe3',
                        borderwidth=1, relief="solid", show="*",
                        font=("Times New Roman", 14, "bold"))
        entry.pack(side="left", ipady=5)

        try:
            eye_path = os.path.join("images", "eye.png")
            eye_img = Image.open(eye_path).resize((20, 20), Image.LANCZOS)
            eye_photo = ImageTk.PhotoImage(eye_img)
        except FileNotFoundError:
            eye_img = Image.new('RGB', (20,20), 'gray')
            eye_photo = ImageTk.PhotoImage(eye_img)
            print(f"Warning: eye.png not found. Using placeholder.")

        eye_label = Label(container, image=eye_photo, bg="white", cursor="hand2")
        eye_label.image = eye_photo
        eye_label.pack(side="left", padx=(5, 0))
        eye_label.bind("<Button-1>", lambda e, entry_widget=entry: self.toggle_password(entry_widget, eye_label))

        return entry

    def toggle_password(self, entry_widget, eye_label):
        if entry_widget.cget("show") == "*":
            entry_widget.config(show="")
        else:
            entry_widget.config(show="*")

    def validate_signup(self):
        username = self.entry_username.get().strip()
        email = self.entry_email.get().strip()
        password = self.entry_password.get().strip()
        confirm = self.entry_confirm.get().strip()

        if not username or not email or not password or not confirm:
            messagebox.showerror("Error", "All fields are required!", parent=self)
            return

        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "Please enter a valid email address.", parent=self)
            return

        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long.", parent=self)
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match!", parent=self)
            return

        # Call signup_user and get the user_id back
        success, message, user_id = self.signup_user(email, username, password) # <--- Modified to receive user_id
        
        if success:
            messagebox.showinfo("Success", message, parent=self)
            # After successful signup, set the current_user_id in the controller
            # and then navigate. This is crucial for SihatiForm.
            self.controller.current_user_id = user_id # <--- Set user_id in controller
            self.controller.show_frame("SihatiForm") # Go to SihatiForm
            # Clear fields after successful signup
            self.entry_username.delete(0, tk.END)
            self.entry_email.delete(0, tk.END)
            self.entry_password.delete(0, tk.END)
            self.entry_confirm.delete(0, tk.END)
        else:
            messagebox.showerror("Error", message, parent=self)

    def signup_user(self, email, username, password):
        try:
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt)
        except Exception as e:
            print(f"Error hashing password: {e}")
            return False, "Error processing password.", None # <--- Return None for user_id

        conn = None # Initialize conn
        try:
            conn = sqlite3.connect("myapp.db") # <--- Use myapp.db consistently
            cursor = conn.cursor()
            
            cursor.execute("INSERT INTO Users (username, email, password) VALUES (?, ?, ?)",
                            (username, email, hashed_password))
            
            user_id = cursor.lastrowid # <--- Get the last inserted row ID (the user_id)
            conn.commit()
            return True, "Account created successfully! Please proceed to the next step.", user_id # <--- Return user_id
        except sqlite3.IntegrityError as e:
            if "username" in str(e).lower():
                return False, "Username already exists. Please choose a different one.", None
            elif "email" in str(e).lower():
                return False, "Email address already registered. Please use a different one or login.", None
            else:
                print(f"Database IntegrityError: {e}")
                return False, "A user with this username or email may already exist.", None
        except sqlite3.Error as e:
            print(f"Database error during signup: {e}")
            return False, f"Database error: {e}", None
        finally:
            if conn:
                conn.close()
