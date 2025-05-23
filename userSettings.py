import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter
import os
import bcrypt # Needed for password verification

# Import all database functions from your db_operations.py
from db_operations import (
    get_user_info_db,
    update_user_info_db,
    save_emergency_contact_db,
    get_emergency_contact_db # Added for completeness if you want to display current contact
)

# === Theme Colors ===
BG_COLOR = "#a3dbe4"  # Background color
TEXT_COLOR = "#333333"  # Text color
LOGOUT_COLOR = "#b19cd9"  # Logout button color
BUTTON_COLOR = "#b19cd9"  # Default button color
BUTTON_TEXT_COLOR = "white"  # Button text color
HIGHLIGHT_COLOR = "white"  # Purple for highlighting
FONT = ("Arial", 12)


class ResponsiveBackground:
    def __init__(self, window, image_path):
        self.window = window
        self.image_path = image_path
        self.last_size = (0, 0)
        
        try:
            # Check if the image file exists
            if os.path.exists(image_path):
                self.original_image = Image.open(image_path)
                print(f"Loaded image: {image_path}")
                self.update_background()
                self.window.bind("<Configure>", self.on_window_resize)
            else:
                print(f"Error: Background image not found at {image_path}. Using solid background color.")
                window.configure(bg="#48bfe3") # Fallback to solid color
        except Exception as e:
            print(f"Error loading image: {e}")
            window.configure(bg="#48bfe3") # Fallback in case of PIL errors


    def on_window_resize(self, event):
        # Only update if the size has significantly changed
        current_size = (self.window.winfo_width(), self.window.winfo_height())
        if abs(current_size[0] - self.last_size[0]) > 10 or \
           abs(current_size[1] - self.last_size[1]) > 10:
            self.last_size = current_size
            self.update_background()

    def update_background(self):
        if not hasattr(self, 'original_image'): # If image failed to load
            return

        try:
            width = self.window.winfo_width()
            height = self.window.winfo_height()

            if width > 0 and height > 0:
                resized_image = self.original_image.resize((width, height), Image.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(resized_image)

                if hasattr(self, 'bg_label'):
                    self.bg_label.config(image=self.bg_photo)
                else:
                    self.bg_label = tk.Label(self.window, image=self.bg_photo)
                    self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                    self.bg_label.lower() # Ensure background label is always behind other widgets
        except Exception as e:
            print(f"Error updating background: {e}")


class UserPage(tk.Frame):
    def __init__(self, parent, controller, user_id=None):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.user_id = user_id  # This will be set by the controller.show_frame method
        self.configure(bg=BG_COLOR)

        # Home Button
        self.home_btn = tk.Button(
            self,
            text="🏠 Home",
            font=("Arial", 14, "bold"),
            bg="#48bfe3",
            fg="#ffffff",
            relief="flat",
            command=lambda: controller.show_frame("homepage")
        )
        self.home_btn.place(x=10, y=10)

        self.language = tk.StringVar(value="English")
        self.notifications_on = True
        
        self.bg_responsive = ResponsiveBackground(self, "images/bgForm.png")
        
        # We need to call create_widgets only after the frame is fully rendered
        # and has a non-zero size for the background to correctly apply.
        # Placing it in after(100) is a good practice.
        self.after(100, self.create_widgets)

    def create_widgets(self):
        # Create a frame to hold all the widgets on top of the background
        profile_frame = tk.Frame(self, bg=HIGHLIGHT_COLOR, width=350, height=500, bd=5, relief=tk.RAISED)
        profile_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(profile_frame, text="User Settings", font=("Arial", 24, "bold"), fg="black", bg=HIGHLIGHT_COLOR).pack(pady=20)
        
        # Use lambda functions to pass arguments to the methods if needed later
        self.create_section("👤 Profile", self.open_profile, profile_frame, highlight="black").pack(fill=tk.X, padx=20, pady=10)
        self.create_section("⚙️ Settings", self.open_settings, profile_frame, highlight="black").pack(fill=tk.X, padx=20, pady=10)
        self.create_section("❓ Help & Support", self.open_help, profile_frame, highlight="black").pack(fill=tk.X, padx=20, pady=10)
        self.create_section("🔒 Privacy & Security", self.open_privacy, profile_frame, highlight="black").pack(fill=tk.X, padx=20, pady=10)
        self.create_section("☎️ Emergency Contact", self.add_emergency_contact, profile_frame, highlight="black").pack(fill=tk.X, padx=20, pady=10)

        # Ensure the logout button is at the bottom of the frame
        tk.Button(profile_frame, text="Log Out", fg="white", bg=LOGOUT_COLOR, font=("Arial", 16, "bold"),
                    command=self.logout, height=3, width=20, bd=0, relief=tk.FLAT).pack(fill=tk.X, padx=50, pady=20)

    def create_section(self, text, command, parent, highlight=None):
        frame = tk.Frame(parent, bg="white", height=60, bd=0)
        frame.pack_propagate(False)

        button = tk.Button(frame, text=text, font=("Arial", 14), fg=highlight or BG_COLOR, bg="white", bd=0, command=command,
                                height=2, width=20, relief="solid", borderwidth=2, padx=20, pady=10)
        button.pack(side=tk.TOP, padx=20, pady=10)

        return frame

    def open_settings(self):
        settings_win = tk.Toplevel(self)
        settings_win.title("Settings")
        settings_win.geometry("300x250")
        settings_win.configure(bg=BG_COLOR)

        # Language Option
        tk.Label(settings_win, text="Language:", font=FONT, fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=(10, 0))
        languages = ["English", "Arabic", "French"]
        for lang in languages:
            rb = tk.Radiobutton(
                settings_win, text=lang, variable=self.language, value=lang,
                font=FONT, fg=TEXT_COLOR, bg=BG_COLOR,
                selectcolor=BG_COLOR, activebackground=BG_COLOR
            )
            rb.pack(anchor="w", padx=30)

        # Notifications Toggle
        tk.Label(settings_win, text="Notifications:", font=FONT, fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=(20, 5))

        notif_btn = tk.Button(settings_win, font=FONT, width=8, relief="flat", fg="white")
        notif_btn.pack(pady=5)

        def toggle_notifications():
            self.notifications_on = not self.notifications_on
            notif_btn.config(
                text="ON" if self.notifications_on else "OFF",
                bg="green" if self.notifications_on else "red"
            )

        # Initial button state
        notif_btn.config(
            text="ON" if self.notifications_on else "OFF",
            bg="green" if self.notifications_on else "red",
            command=toggle_notifications
        )

        # Close button
        tk.Button(settings_win, text="Close", command=settings_win.destroy,
                    bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR,
                    font=FONT, relief="flat", padx=10, pady=5).pack(pady=20)

    def open_profile(self):
        # Ensure user_id is set before attempting to load data
        if self.controller.current_user_id is None:
            messagebox.showerror("Error", "No user logged in. Please log in first.")
            self.controller.show_frame("LogSign") # Redirect to login page
            return
            
        self.user_id = self.controller.current_user_id # Ensure UserPage has the current user_id

        user, form = get_user_info_db(self.user_id) # Use the DB function from db_operations
        if not user:
            messagebox.showerror("Error", "User profile data not found.")
            return

        username, email, _ = user # password is not needed for display
        
        # Ensure 'form' has enough elements, including 'medications'
        # Default empty values if form is None or too short
        form_data = form if form else ("", "", "", "", 0, 0, 0, "") # Added empty string for medications
        
        # Unpack based on the Forms table structure
        weight, height, age, blood_type, diabetes, bp, heart, medications = form_data

        win = tk.Toplevel(self)
        win.title("Profile")
        win.geometry("400x500")
        win.configure(bg=BG_COLOR)

        canvas = tk.Canvas(win, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_COLOR)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(scroll_frame, text="👤 Profile", font=("Arial", 20, "bold"), bg=BG_COLOR, fg="white").pack(pady=(20, 10))

        def label_row(label_text, value_text):
            row = tk.Frame(scroll_frame, bg="white")
            row.pack(padx=20, pady=8, fill="x")

            label_widget = tk.Label(row, text=label_text, font=("Arial", 12, "bold"), fg=TEXT_COLOR, bg="white")
            label_widget.pack(side="left", padx=10, pady=(5, 0))

            value_widget = tk.Label(row, text=value_text, font=("Arial", 12), fg=TEXT_COLOR, bg="white")
            value_widget.pack(side="left", padx=10, pady=(0, 5))

            row.pack_configure(anchor="center")

        label_row("Username", username)
        label_row("Email", email)
        label_row("Weight", f"{weight} Kg" if weight else "N/A")
        label_row("Height", f"{height} Cm" if height else "N/A")
        label_row("Age", age if age else "N/A")
        label_row("Blood Type", blood_type if blood_type else "N/A")

        conditions = []
        if diabetes: conditions.append("Diabetes")
        if bp: conditions.append("High Blood Pressure")
        if heart: conditions.append("Heart Disease")
        label_row("Conditions", ", ".join(conditions) if conditions else "None")
        label_row("Medications", medications if medications else "None") # Display medications

        tk.Button(scroll_frame, text="Edit Profile", font=("Arial", 12, "bold"),
                    bg=BUTTON_COLOR, fg="white", cursor="hand2",
                    command=lambda: self.edit_profile(user, form_data, win)).pack(pady=20)

    def edit_profile(self, user_data_from_db, form_data_from_db, parent_profile_window):
        username, email, current_password_hash = user_data_from_db
        weight, height, age, blood_type, diabetes, bp, heart, medications = form_data_from_db

        win = tk.Toplevel(self)
        win.title("Edit Profile")
        win.geometry("350x650") # Adjusted height for new medication field and better spacing
        win.configure(bg=BG_COLOR)

        def entry_field(parent_frame, label_text, initial_value, is_password=False):
            tk.Label(parent_frame, text=label_text, font=("Arial", 12), fg="white", bg=BG_COLOR).pack(pady=(5,0))
            entry = tk.Entry(parent_frame, font=("Arial", 12), show="*" if is_password else "")
            entry.insert(0, initial_value)
            entry.pack(pady=2)
            return entry

        username_entry = entry_field(win, "Username", username)
        # Email is usually changed in Privacy & Security, but if you want it here:
        # email_entry = entry_field(win, "Email", email) 
        
        # For simplicity in this edit, we'll assume password and email are handled in Privacy
        # If you want to allow password change here, you'd need current password verification.
        
        weight_entry = entry_field(win, "Weight (Kg)", weight)
        height_entry = entry_field(win, "Height (Cm)", height)
        age_entry = entry_field(win, "Age", age)

        tk.Label(win, text="Blood Type", font=("Arial", 12), fg="white", bg=BG_COLOR).pack(pady=(5,0))
        blood_var = tk.StringVar(value=blood_type if blood_type else "A") # Default if empty
        tk.OptionMenu(win, blood_var, "A", "B", "AB", "O").pack(pady=2)

        diabetes_var = tk.IntVar(value=diabetes)
        bp_var = tk.IntVar(value=bp)
        heart_var = tk.IntVar(value=heart)

        tk.Checkbutton(win, text="Diabetes", variable=diabetes_var, bg=BG_COLOR, font=FONT, fg="white", selectcolor=BG_COLOR).pack(pady=2)
        tk.Checkbutton(win, text="High Blood Pressure", variable=bp_var, bg=BG_COLOR, font=FONT, fg="white", selectcolor=BG_COLOR).pack(pady=2)
        tk.Checkbutton(win, text="Heart Disease", variable=heart_var, bg=BG_COLOR, font=FONT, fg="white", selectcolor=BG_COLOR).pack(pady=2)

        # New field for medications
        medications_entry = entry_field(win, "Medications (e.g., Insulin, Metformin)", medications)

        def save():
            new_username = username_entry.get().strip()
            new_weight = weight_entry.get().strip()
            new_height = height_entry.get().strip()
            new_age = age_entry.get().strip()
            new_blood_type = blood_var.get()
            new_diabetes = diabetes_var.get()
            new_bp = bp_var.get()
            new_heart = heart_var.get()
            new_medications = medications_entry.get().strip()

            if not new_username:
                messagebox.showerror("Input Error", "Username cannot be empty.")
                return

            # Keep original email and password hash for update, as they are not edited here
            success, msg = update_user_info_db(
                self.user_id,
                new_username, email, current_password_hash,
                new_weight, new_height, new_age,
                new_blood_type, new_diabetes, new_bp, new_heart,
                new_medications
            )
            if success:
                messagebox.showinfo("Updated", msg)
                win.destroy()
                parent_profile_window.destroy() # Close the profile display window to refresh
                # You might want to automatically re-open the profile view after update
                self.open_profile() # Re-open to show updated data
            else:
                messagebox.showerror("Error", msg)

        tk.Button(win, text="Save Changes", font=("Arial", 12, "bold"), bg=BUTTON_COLOR, fg="white", command=save).pack(pady=15)

    def open_privacy(self):
        def verify_current_password_and_then(action_function):
            verify_win = tk.Toplevel(self)
            verify_win.title("Verify Password")
            verify_win.geometry("250x150")
            verify_win.configure(bg=BG_COLOR)

            tk.Label(verify_win, text="Enter Current Password", bg=BG_COLOR, fg="white", font=FONT).pack(pady=10)
            entry = tk.Entry(verify_win, show="*", font=FONT)
            entry.pack(pady=5)

            def check_password():
                # Get current password hash from DB
                user_info, _ = get_user_info_db(self.user_id)
                if not user_info:
                    messagebox.showerror("Error", "Could not retrieve user info.")
                    verify_win.destroy()
                    return

                db_password_hash = user_info[2] # password is the 3rd element (index 2)
                entered_password = entry.get().encode('utf-8')

                if bcrypt.checkpw(entered_password, db_password_hash):
                    verify_win.destroy()
                    action_function()
                else:
                    messagebox.showerror("Error", "Incorrect password.")

            tk.Button(verify_win, text="Verify", bg=BUTTON_COLOR, fg="white", command=check_password, font=FONT).pack(pady=10)

        def change_email_form():
            new_win = tk.Toplevel(self)
            new_win.title("Change Email")
            new_win.geometry("300x200")
            new_win.configure(bg=BG_COLOR)

            tk.Label(new_win, text="New Email", bg=BG_COLOR, fg="white", font=FONT).pack(pady=10)
            entry = tk.Entry(new_win, font=FONT)
            entry.pack(pady=5)

            def save_new_email():
                new_email = entry.get().strip()
                if not new_email:
                    messagebox.showerror("Input Error", "Email cannot be empty.")
                    return
                
                # Fetch current user data to pass to update_user_info_db
                user_info, form_info = get_user_info_db(self.user_id)
                if not user_info:
                    messagebox.showerror("Error", "Could not retrieve user info.")
                    new_win.destroy()
                    return

                username, _, current_password_hash = user_info # Get username and password hash
                
                # Pass current form info, even if not changed, to update_user_info_db
                form_data = form_info if form_info else ("", "", "", "", 0, 0, 0, "")

                success, msg = update_user_info_db(
                    self.user_id, username, new_email, current_password_hash,
                    *form_data # Unpack existing form data
                )
                if success:
                    messagebox.showinfo("Updated", msg)
                    new_win.destroy()
                else:
                    messagebox.showerror("Error", msg)

            tk.Button(new_win, text="Save", bg=BUTTON_COLOR, fg="white", command=save_new_email, font=FONT).pack(pady=10)

        def change_password_form():
            new_win = tk.Toplevel(self)
            new_win.title("Change Password")
            new_win.geometry("300x250")
            new_win.configure(bg=BG_COLOR)

            tk.Label(new_win, text="New Password", bg=BG_COLOR, fg="white", font=FONT).pack(pady=10)
            new_pass_entry = tk.Entry(new_win, show="*", font=FONT)
            new_pass_entry.pack(pady=5)

            tk.Label(new_win, text="Confirm New Password", bg=BG_COLOR, fg="white", font=FONT).pack(pady=10)
            confirm_pass_entry = tk.Entry(new_win, show="*", font=FONT)
            confirm_pass_entry.pack(pady=5)

            def save_new_password():
                new_password = new_pass_entry.get()
                confirm_password = confirm_pass_entry.get()

                if new_password != confirm_password:
                    messagebox.showerror("Error", "Passwords do not match!")
                    return
                if not new_password:
                    messagebox.showerror("Error", "Password cannot be empty!")
                    return

                hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                
                # Fetch current user data to pass to update_user_info_db
                user_info, form_info = get_user_info_db(self.user_id)
                if not user_info:
                    messagebox.showerror("Error", "Could not retrieve user info.")
                    new_win.destroy()
                    return

                username, email, _ = user_info # Get username and email
                 # Pass current form info, even if not changed, to update_user_info_db
                form_data = form_info if form_info else ("", "", "", "", 0, 0, 0, "")

                success, msg = update_user_info_db(
                    self.user_id, username, email, hashed_new_password,
                    *form_data # Unpack existing form data
                )
                if success:
                    messagebox.showinfo("Updated", "Password updated successfully!")
                    new_win.destroy()
                else:
                    messagebox.showerror("Error", msg)

            tk.Button(new_win, text="Save", bg=BUTTON_COLOR, fg="white", command=save_new_password, font=FONT).pack(pady=10)

        privacy_win = tk.Toplevel(self) # Renamed to avoid conflict with 'win' from open_profile
        privacy_win.title("Privacy & Security")
        privacy_win.geometry("300x250")
        privacy_win.configure(bg=BG_COLOR)

        tk.Button(privacy_win, text="Change Email", font=("Arial", 12, "bold"), bg=BUTTON_COLOR, fg="white", command=lambda: verify_current_password_and_then(change_email_form)).pack(pady=20)
        tk.Button(privacy_win, text="Change Password", font=("Arial", 12, "bold"), bg=BUTTON_COLOR, fg="white", command=lambda: verify_current_password_and_then(change_password_form)).pack(pady=5)

    def open_help(self):
        help_win = tk.Toplevel(self)
        help_win.title("Help & Support")
        help_win.geometry("400x300")
        help_win.configure(bg=BG_COLOR)

        canvas = tk.Canvas(help_win, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(help_win, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        content_frame = tk.Frame(canvas, bg=BG_COLOR)

        window_id = canvas.create_window((0, 0), window=content_frame, anchor="n", width=380)

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        content_frame.bind("<Configure>", on_frame_configure)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(content_frame, text="Help & Support", font=("Arial", 18, "bold"), fg="black", bg=BG_COLOR).pack(pady=10)

        help_text = (
            "Welcome to Sihati! Here's how to use the app:\n\n"
            "📏 Measurements: Input your weight, height, age, and blood type in the Profile section.\n\n"
            "💊 Medicine Reminders: Set reminders in the medicine section (available on main menu).\n\n"
            "☎️ Emergency Contact: Save a contact in case of health emergencies.\n\n"
            "⚙️ Settings: Change your language and toggle notifications.\n\n"
            "🔒 Privacy: Update your email and password securely.\n\n"
            "If you have further issues, please contact support@sihatiapp.com."
        )

        tk.Label(content_frame, text=help_text, font=("Arial", 12), fg="black", bg=BG_COLOR, wraplength=360, justify="left").pack(pady=10) # Changed justify

        tk.Button(content_frame, text="Close", font=("Arial", 12, "bold"), bg=BUTTON_COLOR, fg="white", command=help_win.destroy).pack(pady=10)

    def add_emergency_contact(self):
        win = tk.Toplevel(self)
        win.title("Add Emergency Contact")
        win.geometry("350x250")
        win.configure(bg=BG_COLOR)

        tk.Label(win, text="Emergency Contact Name", font=FONT, fg="white", bg=BG_COLOR).pack(pady=10)
        name_entry = tk.Entry(win, font=FONT)
        name_entry.pack(pady=5)

        tk.Label(win, text="Emergency Contact Number", font=FONT, fg="white", bg=BG_COLOR).pack(pady=10)
        number_entry = tk.Entry(win, font=FONT)
        number_entry.pack(pady=5)
        
        # Optionally, load existing contact if it exists
        existing_contact = get_emergency_contact_db(self.user_id)
        if existing_contact:
            name_entry.insert(0, existing_contact[0])
            number_entry.insert(0, existing_contact[1])

        def save():
            name = name_entry.get().strip()
            number = number_entry.get().strip()
            if not name or not number:
                messagebox.showerror("Input Error", "Name and number cannot be empty.")
                return

            save_emergency_contact_db(self.user_id, name, number) # Use the DB function from db_operations
            messagebox.showinfo("Saved", "Emergency contact added successfully!")
            win.destroy()

        tk.Button(win, text="Save", font=("Arial", 12, "bold"), bg=BUTTON_COLOR, fg="white", command=save).pack(pady=20)

    def logout(self):
        # Clear the current user ID when logging out
        self.controller.set_current_user_id(None) 
        messagebox.showinfo("Logged Out", "You have been logged out.")
        self.controller.show_frame("LogSign") # Go back to login/signup page