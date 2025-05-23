import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime, timedelta
from plyer import notification
import threading
from PIL import Image, ImageTk
import random

class ReminderFrame(ctk.CTkFrame):
    def __init__(self, parent, controller=None, **kwargs):
        super().__init__(parent, fg_color="#5ab8c2", **kwargs)
        self.controller = controller
        self.parent = parent

        self.bg_photo = None

        # Canvas to hold background image and widgets
        self.canvas = ctk.CTkCanvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.on_resize)

        self.setup_db()
        self.setup_styles()
        self.setup_variables()

        self.create_ui()  # Create UI once initially

        self.check_reminders()
        self.send_dua_periodically()

    def setup_styles(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

    def setup_variables(self):
        # Persistent variables for UI fields
        self.type_var = tk.StringVar()
        self.detail_var = tk.StringVar()
        self.text_detail_var = tk.StringVar()
        self.hour_var = tk.StringVar(value="00")
        self.minute_var = tk.StringVar(value="00")
        self.repeat_var = tk.IntVar()
        self.type_var.trace_add("write", self.update_detail_visibility)

    def setup_db(self):
        with sqlite3.connect("reminders.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS reminders (
                                id INTEGER PRIMARY KEY,
                                type TEXT,
                                detail TEXT,
                                date TEXT,
                                time TEXT)''')
            conn.commit()

    def on_resize(self, event):
        # Resize background image
        try:
            original_image = Image.open(r"images/BACK.jpg")
            resized_image = original_image.resize((event.width, event.height), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(resized_image)
            self.canvas.delete("background")
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw", tags="background")

            # Recreate UI widgets on top of canvas (delete old ones first)
            self.canvas.delete("widgets")
            self.create_ui()
        except Exception as e:
            print(f"Error loading background image: {e}")

    def create_ui(self):
        # Add home button on canvas (using normal Tk button, could also use ctk)
        homeb = tk.Button(self.canvas, text="🏠 Home", background="#48bfe3", foreground="#ffffff",
                          font=("Arial", 14, "bold"), width=11, command=self.go_home)
        homeb.place(x=10, y=10)

        # Frame on right side for input form
        frame_x = max(self.parent.winfo_width() - 250, 250)  # avoid negative or too small position
        frame_y = self.parent.winfo_height() // 2 + 20
        frame = ctk.CTkFrame(self.canvas, fg_color="#ffffff", border_width=3, corner_radius=15)
        self.canvas.create_window(frame_x, frame_y, window=frame, width=480, height=500, tags="widgets")

        ctk.CTkLabel(frame, text="➕ 𝓪𝓭𝓭 𝓻𝓮𝓶𝓲𝓷𝓭𝓮𝓻𝓼", font=("Poppins", 22, "bold"),
                     text_color="#48bfe3").pack(pady=10)

        ctk.CTkLabel(frame, text="Type:", font=("Poppins", 15, "bold"), text_color="#48bfe3").pack(pady=5)

        types = ["🗓️Appointment", "📏    Measurement", " 💊    Medication"]
        values = ["Appointment", "Measurement", "Medication"]

        for text, value in zip(types, values):
            ctk.CTkRadioButton(frame, text=text, variable=self.type_var, value=value,
                               font=("Poppins", 22), text_color="#48bfe3").pack(anchor="w", padx=10)

        detail_frame = ctk.CTkFrame(frame, fg_color="#ffffff")
        detail_frame.pack(pady=10, fill="x", padx=10)
        ctk.CTkLabel(detail_frame, text="Details (Tip):", font=("Poppins", 16, "bold"),
                     text_color="#48bfe3", width=140).pack(side="left")

        # Save these as instance vars so update_detail_visibility can access them
        self.detail_combobox = ctk.CTkComboBox(detail_frame, variable=self.detail_var, font=("Poppins", 20),
                                               values=["Drink Water", "Take Medicine", "Check Blood Pressure",
                                                       "Eat Healthy Meal", "Exercise", "Monitor Blood Sugar",
                                                       "Get Enough Sleep", "Take a Walk"])

        self.detail_entry = ctk.CTkEntry(detail_frame, textvariable=self.text_detail_var, font=("Poppins", 20))

        # Initially show combobox, hide entry
        if self.type_var.get() == "Appointment":
            self.detail_combobox.pack_forget()
            self.detail_entry.pack(side="left", fill="x", expand=True)
        else:
            self.detail_entry.pack_forget()
            self.detail_combobox.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(frame, text="Select Date:", font=("Poppins", 16, "bold"), text_color="#48bfe3").pack(pady=5)
        self.date_entry = DateEntry(frame, width=20, font=("Poppins", 15), background='#48bfe3',
                                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd',
                                    mindate=datetime.now().date())
        self.date_entry.pack(pady=5)

        ctk.CTkLabel(frame, text="Select Time:", font=("Poppins", 16, "bold"), text_color="#48bfe3").pack(pady=5)

        time_frame = ctk.CTkFrame(frame, fg_color="#ffffff", corner_radius=10)
        time_frame.pack(pady=5)

        hours = [f"{i:02d}" for i in range(24)]
        minutes = [f"{i:02d}" for i in range(60)]

        ctk.CTkLabel(time_frame, text="h", font=("Poppins", 14, "bold"), text_color="#48bfe3").pack(side="left", padx=2)
        hour_menu = ctk.CTkOptionMenu(time_frame, variable=self.hour_var, values=hours, font=("Poppins", 14))
        hour_menu.pack(side="left", padx=2)

        ctk.CTkLabel(time_frame, text=":", font=("Poppins", 16, "bold")).pack(side="left")

        minute_menu = ctk.CTkOptionMenu(time_frame, variable=self.minute_var, values=minutes, font=("Poppins", 14))
        minute_menu.pack(side="left", padx=2)
        ctk.CTkLabel(time_frame, text="Min", font=("Poppins", 14, "bold"), text_color="#48bfe3").pack(side="left", padx=2)

        ctk.CTkCheckBox(frame, text="Repeat daily for 3 months", variable=self.repeat_var,
                        font=("Poppins", 19), text_color="#48bfe3").pack(pady=5)

        buttons_frame = ctk.CTkFrame(frame, fg_color="#ffffff")
        buttons_frame.pack(pady=10)

        ctk.CTkButton(buttons_frame, text="➕ Add Reminder", command=self.add_reminder,
                      width=120, height=40, font=("Poppins", 15, "bold")).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="🔄 Clear", command=self.clear_fields,
                      width=120, height=40, font=("Poppins", 15, "bold")).pack(side="left", padx=5)

    def update_detail_visibility(self, *args):
        selected_type = self.type_var.get()
        if selected_type == "Appointment":
            self.detail_combobox.pack_forget()
            self.detail_entry.pack(side="left", fill="x", expand=True)
        else:
            self.detail_entry.pack_forget()
            self.detail_combobox.pack(side="left", fill="x", expand=True)

    def clear_fields(self):
        # Reset variables instead of recreating UI
        self.type_var.set("")
        self.detail_var.set("")
        self.text_detail_var.set("")
        self.hour_var.set("00")
        self.minute_var.set("00")
        self.repeat_var.set(0)
        self.date_entry.set_date(datetime.now().date())

    def go_home(self):
        if self.controller:
            self.controller.show_frame("homepage")
        self.clear_fields()

    def add_reminder(self):
        reminder_type = self.type_var.get()
        detail = self.text_detail_var.get().strip() if reminder_type == "Appointment" else self.detail_var.get().strip()
        base_date = self.date_entry.get()
        reminder_time = f"{self.hour_var.get()}:{self.minute_var.get()}"

        if not reminder_type:
            messagebox.showwarning("Warning", "Please select a type!")
            return

        if not detail:
            messagebox.showwarning("Warning", "Please provide the detail!")
            return

        try:
            base_datetime = datetime.strptime(f"{base_date} {reminder_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Error", "Invalid date or time format!")
            return

        if base_datetime < datetime.now():
            messagebox.showerror("Error", "Cannot set reminders for past times!")
            return

        repeat = self.repeat_var.get()
        with sqlite3.connect("reminders.db") as conn:
            cursor = conn.cursor()
            if repeat:
                for day in range(0, 30 * 11):  # approx 11 months
                    new_date = (base_datetime + timedelta(days=day)).strftime("%Y-%m-%d")
                    cursor.execute("INSERT INTO reminders (type, detail, date, time) VALUES (?, ?, ?, ?)",
                                   (reminder_type, detail, new_date, reminder_time))
            else:
                cursor.execute("INSERT INTO reminders (type, detail, date, time) VALUES (?, ?, ?, ?)",
                               (reminder_type, detail, base_date, reminder_time))
            conn.commit()

        messagebox.showinfo("Success", "Reminder(s) added successfully!")
        self.clear_fields()

    def check_reminders(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with sqlite3.connect("reminders.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reminders WHERE date || ' ' || time = ?", (now,))
            reminders = cursor.fetchall()

        for reminder in reminders:
            threading.Thread(target=self.send_notification, args=(reminder,)).start()

        self.after(60000, self.check_reminders)

    def send_notification(self, reminder):
        type_icons = {
            "Appointment": "🔔",
            "Measurement": "🔗",
            "Medication": "💊"
        }
        icon = type_icons.get(reminder[1], "🔔")
        try:
            notification.notify(
                title=f"{icon} {reminder[1]} Reminder",
                message=f"{reminder[2]}\nDate: {reminder[3]}\nTime: {reminder[4]}",
                timeout=15
            )
        except Exception as e:
            print(f"Error sending notification: {e}")

    def send_dua_periodically(self):
        dua_message = random.choice([
            "اللهم اجعلنا من أهل الجنة.",
            "اللهم شفاءً لا يغادر سقماً.",
            "اللهم بارك لنا في صحتنا وعافيتنا."
        ])
        try:
            notification.notify(
                title="دعاء اليوم",
                message=dua_message,
                timeout=10
            )
        except Exception as e:
            print(f"Error sending dua: {e}")
        self.after(86400000, self.send_dua_periodically)
