import tkinter as tk
import sqlite3
from PIL import ImageTk, Image
import datetime

class ResponsiveBackground:
    def __init__(self, window, image_path):
        self.window = window
        self.image_path = image_path
        self.last_size = (0, 0)

        try:
            self.original_image = Image.open(image_path)
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

class ReminderHistoryApp(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.title = "Reminder History"
        self.configure(bg="white")

        try:
            self.bg_handler = ResponsiveBackground(self, "images/bgReminderHistory.jpg")
        except:
            self.configure(bg="#48bfe3")

        self.buttons = {
            "Appointment": "📅 Appointment",
            "Medication": "💊 Medication",
            "Measurement": "🌡 Measurement"
        }
        self.task_lists = {category: [] for category in self.buttons.keys()}
        self.list_frames = {}
        self.category_visibility = {category: True for category in self.buttons.keys()}

        self.create_widgets()
        self.update_display()
        self.auto_reload()

    def auto_reload(self):
        self.update_display()
        self.after(30000, self.auto_reload)

    def reload_data(self):
        self.update_display()

    def create_widgets(self):
        self.main_frame = tk.Frame(self, bg="white", bd=2, relief=tk.GROOVE)
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=500)

        self.home_button = tk.Button(self, text="🏠 Home", bg="#48bfe3", fg="white",
                                     font=("Arial", 14, "bold"), width=11,
                                     command=lambda: self.controller.show_frame("homepage"))
        self.home_button.place(x=10, y=7)

        self.reload_button = tk.Button(self, text="🔄", bg="#b19cd9", fg="white",
                                       font=("Arial", 14, "bold"), width=5, command=self.reload_data)
        self.reload_button.place(x=155, y=7)

        self.title_label = tk.Label(self.main_frame,
                                    text="Reminder History",
                                    fg="#48bfe3",
                                    bg="white",
                                    font=("MVboli", 30, "bold"))
        self.title_label.pack(pady=10)

        self.canvas = tk.Canvas(self.main_frame, bg="white", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.content_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.content_frame.bind("<Configure>", self.on_frame_configure)

        colors = {
            "Appointment": "#005A9C",
            "Medication": "#2D68C4",
            "Measurement": "#4682B4"
        }

        for category, header_text in self.buttons.items():
            category_container = tk.Frame(self.content_frame, bg="white")
            category_container.pack(fill="x", pady=5)

            header_frame = tk.Frame(category_container, bg="white", padx=10)
            header_frame.pack(fill="x")

            color_bar = tk.Frame(header_frame, bg=colors[category], width=10, height=40)
            color_bar.pack(side="left", fill="y")

            header_label = tk.Label(header_frame,
                                    text=header_text,
                                    font=("Arial", 19, "bold"),
                                    bg="#f0f0f0",
                                    fg="#48bfe3",
                                    anchor="w",
                                    padx=10,
                                    pady=5)
            header_label.pack(side="left", fill="x", expand=True)

            list_frame = tk.Frame(category_container, bg="white", bd=1, relief=tk.GROOVE)
            list_frame.pack(fill="x", pady=(5, 10), padx=10)

            self.list_frames[category] = list_frame

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.center_content()

    def center_content(self):
        self.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        frame_width = self.content_frame.winfo_reqwidth()
        if canvas_width > frame_width:
            self.canvas.itemconfigure(1, width=canvas_width)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def fetch_reminders(self):
        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")

        with sqlite3.connect("reminders.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT type, detail, date, time FROM reminders 
                WHERE 
                    (DATE(date) = ? AND time <= ?) OR  
                    DATE(date) = DATE(?, '-1 day') OR
                    DATE(date) = DATE(?, '+1 day')     
                ORDER BY date DESC, time DESC
            """, (current_date, current_time, current_date, current_date))
            return cursor.fetchall()

    def update_display(self):
        reminders = self.fetch_reminders()

        for category in self.task_lists:
            for widget in self.task_lists[category]:
                widget.destroy()
            self.task_lists[category].clear()

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)
        now = datetime.datetime.now().time()

        categorized = {category: [] for category in self.buttons.keys()}
        for reminder_type, detail, date_str, time_str in reminders:
            if reminder_type in categorized:
                try:
                    reminder_time = datetime.datetime.strptime(time_str, "%H:%M").time()
                    reminder_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    if (reminder_date == today and reminder_time <= now) or reminder_date == yesterday or reminder_date == tomorrow:
                        categorized[reminder_type].append((detail, date_str, time_str))
                except ValueError:
                    continue

        for category, items in categorized.items():
            if category in self.list_frames:
                for widget in self.list_frames[category].winfo_children():
                    widget.destroy()

                if not items:
                    no_label = tk.Label(
                        self.list_frames[category],
                        text="❗ No reminders",
                        font=("Arial", 13, "italic"),
                        bg="white", fg="gray"
                    )
                    no_label.pack(fill="x", padx=10, pady=5)
                    self.task_lists[category].append(no_label)
                else:
                    for detail, date_str, time_str in items:
                        try:
                            reminder_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                            reminder_time = datetime.datetime.strptime(time_str, "%H:%M").time()
                        except ValueError:
                            continue

                        is_today = reminder_date == today
                        is_yesterday = reminder_date == yesterday
                        is_tomorrow = reminder_date == tomorrow

                        if is_today:
                            text_color = "black"
                            tag = " Today"
                            tag_bg = "#4CAF50"  # Green
                        elif is_yesterday:
                            text_color = "black"
                            tag = " Yesterday"
                            tag_bg = "#ff6961"  # Red
                        elif is_tomorrow:
                            text_color = "black"
                            tag = " Tomorrow"
                            tag_bg = "#48bfe3"  # Blue
                        else:
                            text_color = "black"
                            tag = ""
                            tag_bg = None

                        readable_date = f"{date_str} at {time_str}"

                        item_frame = tk.Frame(self.list_frames[category], bg="white", padx=10, pady=5)
                        item_frame.pack(fill="x", pady=2)

                        detail_label = tk.Label(
                            item_frame,
                            text=f"- {detail}    🕒 {readable_date}",
                            font=("Arial", 14, "bold"),
                            bg="white",
                            fg=text_color,
                            anchor="w",
                            justify="left",
                            wraplength=450
                        )
                        detail_label.pack(side="left", fill="x", expand=True)

                        if tag:
                            tag_label = tk.Label(
                                item_frame,
                                text=tag,
                                font=("Arial", 10, "bold"),
                                bg=tag_bg,
                                fg="white",
                                padx=5,
                                pady=2,
                                relief=tk.RAISED,
                                bd=1
                            )
                            tag_label.pack(side="right", padx=5)

                        self.task_lists[category].append(item_frame)

        self.content_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))