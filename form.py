# SihatiForm.py
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import ImageTk, Image
import sqlite3 # Still needed if you're using sqlite3.connect directly in save_data/load_existing_data

# Import specific database functions if you were using them directly (not in this case for SihatiForm as much)
# from db_operations import update_user_info, get_user_info # Example if you needed these specific functions
# For SihatiForm, you are connecting directly, which is fine, but db_operations.py is the preferred place for such functions.
# However, for this fix, your existing SQLite logic in SihatiForm is okay as is for now.

# Keep ResponsiveBackground as it is, or move it to its own file if not used elsewhere
class ResponsiveBackground:
    def __init__(self, window, image_path):
        self.window = window
        self.image_path = image_path
        self.last_size = (0, 0) 
        
        try:
            self.original_image = Image.open(image_path)
            print(f"Loaded image: {image_path}") 
            self.update_background()
            self.window.bind("<Configure>", self.on_window_resize)
        except Exception as e:
            print(f"Error loading image: {e}")
            window.configure(bg="#48bfe3")

    def on_window_resize(self, event):
        self.update_background()
        
    def update_background(self):
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
                    self.bg_label.lower()
        except Exception as e:
            print(f"Error updating background: {e}")

class SihatiForm(tk.Frame):
    def __init__(self, parent, controller, user_id=None):
        super().__init__(parent)
        self.controller = controller
        self.user_id = user_id  # Initialize user_id
        print(f"SihatiForm.__init__: Initialized with user_id={self.user_id}") # ADDED PRINT
        self.medications_list = []
        try:
            self.bg_handler = ResponsiveBackground(self, "images/bgForm.png")
        except:
            self.configure(bg="#48bfe3")
        self.setup_ui()
        # self.load_existing_data() # This call needs to be in your controller's show_frame too for updates

    def setup_ui(self):
        self.main_frame = tk.Frame(self, bg="white", padx=30, pady=30, width=550, height=700, highlightthickness=3, highlightbackground="#48bfe3")
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.main_frame.pack_propagate(False)
        tk.Label(self.main_frame, text="Personal Information", font=("Arial", 30, 'bold'), fg="#48bfe3", bg="white").grid(row=0, column=0, columnspan=2, pady=(0, 25))
        tk.Label(self.main_frame, text="Weight (kg):", font=("Arial", 13, "bold"),fg="#48bfe3", bg="white").grid(row=1, column=0, sticky="w", pady=(0, 3))
        self.weight_entry = tk.Entry(self.main_frame, width=20, font=("Arial", 12), justify="center")
        self.weight_entry.grid(row=2, column=0, pady=(0, 13), sticky="ew")
        tk.Label(self.main_frame, text="Height (cm):", font=("Arial", 13, "bold"), fg="#48bfe3",bg="white").grid(row=1, column=1, sticky="w", pady=(0, 3))
        self.height_entry = tk.Entry(self.main_frame, width=20, font=("Arial", 12), justify="center")
        self.height_entry.grid(row=2, column=1, pady=(0, 13), sticky="ew")
        tk.Label(self.main_frame, text="Age:", font=("Arial", 13, "bold"),fg="#48bfe3", bg="white").grid(row=3, column=0, sticky="w", pady=(0, 3))
        self.age_entry = tk.Entry(self.main_frame, width=20, font=("Arial", 12), justify="center")
        self.age_entry.grid(row=4, column=0, pady=(0, 13), sticky="ew")
        tk.Label(self.main_frame, text="Blood Type:", font=("Arial", 13, "bold"),fg="#48bfe3", bg="white").grid(row=3, column=1, sticky="w", pady=(0, 3))
        self.blood_type_var = tk.StringVar()
        self.blood_type_dropdown = ttk.Combobox(self.main_frame, textvariable=self.blood_type_var, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], state="readonly", width=18, font=("Arial", 12))
        self.blood_type_dropdown.grid(row=4, column=1, pady=(0, 13), sticky="ew")
        self.blood_type_dropdown.current(0)
        tk.Label(self.main_frame, text="Health Conditions:", font=("Arial", 13, "bold"), fg="#48bfe3",bg="white").grid(row=5, column=0, columnspan=2, sticky="w", pady=(0, 5))
        self.conditions_frame = tk.Frame(self.main_frame, bg="white")
        self.conditions_frame.grid(row=6, column=0, columnspan=2, sticky="w", pady=(0, 13))
        self.diabetes_var = tk.BooleanVar()
        self.blood_pressure_var = tk.BooleanVar()
        self.heart_disease_var = tk.BooleanVar()
        tk.Checkbutton(self.conditions_frame, text='Diabetes', variable=self.diabetes_var, bg="white", font=("Arial", 13)).pack(anchor="w", pady=2)
        tk.Checkbutton(self.conditions_frame, text='Blood pressure', variable=self.blood_pressure_var, bg="white", font=("Arial", 13)).pack(anchor="w", pady=2)
        tk.Checkbutton(self.conditions_frame, text='Heart disease', variable=self.heart_disease_var, bg="white", font=("Arial", 13)).pack(anchor="w", pady=2)
        tk.Label(self.main_frame, text="Medications:", font=("Arial", 13, "bold"), fg="#48bfe3",bg="white").grid(row=7, column=0, columnspan=2, sticky="w", pady=(0, 5))
        self.med_frame = tk.Frame(self.main_frame, bg="white")
        self.med_frame.grid(row=8, column=0, columnspan=2, sticky="w", pady=(0, 5))
        self.medications_entry = tk.Entry(self.med_frame, width=25, font=("Arial", 12), justify="center")
        self.medications_entry.pack(side=tk.LEFT, padx=(0, 13))
        self.add_med_button = tk.Button(self.med_frame, text="+", command=self.add_medication, font=("Arial", 14, "bold"), bg="#b19cd9", fg="white", width=3)
        self.add_med_button.pack(side=tk.LEFT)
        self.medications_label = tk.Label(self.main_frame, text="None", bg="white", font=("Arial", 13))
        self.medications_label.grid(row=9, column=0, columnspan=2, sticky="w", pady=(0, 20))
        self.save_and_home_button = tk.Button(self.main_frame, text="Save & Go Home", command=lambda:[self.save_data(),self.controller.show_frame("homepage")], font=("Arial", 12, "bold"), bg="#b19cd9", fg="white", width=20)
        self.save_and_home_button.grid(row=14, column=0, columnspan=2, pady=(10, 0))

    def save_data(self):
        print(f"SihatiForm.save_data: self.user_id = {self.user_id}") # ADDED PRINT
        weight = self.weight_entry.get()
        height = self.height_entry.get()
        age = self.age_entry.get()
        blood_type = self.blood_type_var.get()
        diabetes = 1 if self.diabetes_var.get() else 0
        blood_pressure = 1 if self.blood_pressure_var.get() else 0
        heart_disease = 1 if self.heart_disease_var.get() else 0
        medications = ', '.join(self.medications_list)
        try:
            float(weight)
            float(height)
            int(age)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for Weight, Height, and Age.")
            return

        if self.user_id is None:
            messagebox.showerror("Error", "No user is logged in. Cannot save health data.")
            return

        try:
            conn = sqlite3.connect('myapp.db')
            cursor = conn.cursor()
            cursor.execute("SELECT form_id FROM Forms WHERE user_id = ?", (self.user_id,))
            existing_form_id = cursor.fetchone()

            if existing_form_id:
                cursor.execute('''
                    UPDATE Forms
                    SET weight = ?, height = ?, age = ?, blood_type = ?, diabetes = ?, blood_pressure = ?, heart_disease = ?, medications = ?
                    WHERE user_id = ?
                ''', (weight, height, age, blood_type, diabetes, blood_pressure, heart_disease, medications, self.user_id))
                message = "Health information updated successfully!"
            else:
                cursor.execute('''
                    INSERT INTO Forms (user_id, weight, height, age, blood_type, diabetes, blood_pressure, heart_disease, medications)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (self.user_id, weight, height, age, blood_type, diabetes, blood_pressure, heart_disease, medications))
                message = "Health information saved successfully!"

            conn.commit()
            conn.close()
            messagebox.showinfo("Data Saved", message)
            self.clear_fields()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save health information: {e}")
            print(f"Database error: {e}")

    def add_medication(self):
        med = self.medications_entry.get().strip()
        if med and med not in self.medications_list: # Ensure no duplicates
            self.medications_list.append(med)
            self.medications_entry.delete(0, tk.END)
            self.update_medications_display()
        elif med in self.medications_list:
            messagebox.showinfo("Duplicate", f"'{med}' is already in the medications list.")
        self.medications_entry.delete(0, tk.END)


    def update_medications_display(self):
        self.medications_label.config(text=", ".join(self.medications_list) if self.medications_list else "None")
    def clear_fields(self):
        self.weight_entry.delete(0, tk.END)
        self.height_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.medications_entry.delete(0, tk.END)
        self.blood_type_dropdown.current(0)
        self.diabetes_var.set(False)
        self.blood_pressure_var.set(False)
        self.heart_disease_var.set(False)
        self.medications_list = []
        self.update_medications_display()

    def load_existing_data(self):
        """Loads existing health data for the current user into the form fields."""
        print(f"SihatiForm.load_existing_data: self.user_id = {self.user_id}") # ADDED PRINT
        if self.user_id is None:
            print("SihatiForm.load_existing_data: No user_id set, cannot load data.") # ADDED PRINT
            return

        try:
            conn = sqlite3.connect('myapp.db')
            cursor = conn.cursor()
            cursor.execute("SELECT weight, height, age, blood_type, diabetes, blood_pressure, heart_disease, medications FROM Forms WHERE user_id = ?", (self.user_id,))
            data = cursor.fetchone()
            conn.close()

            self.clear_fields() # Clear previous data before loading new
            
            if data:
                weight, height, age, blood_type, diabetes, blood_pressure, heart_disease, medications_str = data
                
                self.weight_entry.insert(0, weight)
                self.height_entry.insert(0, height)
                self.age_entry.insert(0, age)
                self.blood_type_var.set(blood_type)
                
                self.diabetes_var.set(bool(diabetes))
                self.blood_pressure_var.set(bool(blood_pressure))
                self.heart_disease_var.set(bool(heart_disease))
                
                if medications_str:
                    self.medications_list = [m.strip() for m in medications_str.split(',') if m.strip()]
                else:
                    self.medications_list = []
                self.update_medications_display()
                print(f"SihatiForm.load_existing_data: Data loaded for user_id {self.user_id}.") # ADDED PRINT
            else:
                print(f"SihatiForm.load_existing_data: No existing data for user_id {self.user_id}. Keeping fields clear.") # ADDED PRINT

        except sqlite3.Error as e:
            print(f"Error loading existing health data: {e}")
            messagebox.showerror("Database Error", f"Failed to load existing health data: {e}")