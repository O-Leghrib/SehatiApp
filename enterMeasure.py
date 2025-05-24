from locale import windows_locale
from tkinter import *
from tkinter import ttk
from turtle import right
from PIL import Image, ImageTk
from database import insert_measurements


def save_measurements_to_db(measure_type, values_dict, time=None):
    """Saves measurements with context to the database."""
    patient_id = 1  # dynamically set based on the patient's info

    for label, value in values_dict.items():
        try:
            if value >0:

                if "Diabetes" in measure_type:
                    full_measure_type = f"{measure_type}:{label}:{time}"
                else:

                    full_measure_type = f"{measure_type}:{label}"
                insert_measurements(patient_id, full_measure_type, float(value))
        except Exception as e:
            print(f"Error saving {label}: {e}")


import tkinter as tk
from PIL import Image, ImageTk
import customtkinter as ctk


class SehatiApp(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # إعداد المظهر العام لـ customtkinter
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.original_bg_img = Image.open("images/bgEnterMeasures.png")
        self.bg_photo = None

        try:
            self.logo_img = Image.open("logo.png")
            self.logo_photo = ImageTk.PhotoImage(self.logo_img)
        except Exception as e:
            print(f"Error loading logo image: {e}")
            self.logo_photo = None

        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill="both", expand=True)

        # فقط main_frame باستخدام CTkFrame لزوايا ناعمة
        self.main_frame = ctk.CTkFrame(
            self.canvas,
            corner_radius=20,
            fg_color="white",
            border_width=2,
            border_color="#cccccc"
        )
        self.main_window = self.canvas.create_window(0, 0, window=self.main_frame, anchor="e")

        # زر الصفحة الرئيسية (بسيط)
        self.home_button = tk.Button(
            self.canvas,
            text="🏠 Home",
            background="#48bfe3",
            foreground="#ffffff",
            font=("Arial", 14, "bold"),
            width=11,
            command=lambda: controller.show_frame("homepage")
        )
        self.canvas.create_window(30, 30, window=self.home_button, anchor="nw")

        # زر القلب
        self.heart_button = tk.Button(
            self.canvas,
            text="💓Go To Heart",
            background="#48bfe3",
            foreground="#ffffff",
            font=("Arial", 14, "bold"),
            width=18,
            command=lambda: self.show_frame(HeartFrame)
        )
        self.heart_button_window = self.canvas.create_window(0, 0, window=self.heart_button, anchor="center")

        # زر السكري
        self.diabetes_button = tk.Button(
            self.canvas,
            text="🩸Go To Diabetes",
            background="#48bfe3",
            foreground="#ffffff",
            font=("Arial", 14, "bold"),
            width=18,
            command=lambda: self.show_frame(DiabetesFrame)
        )
        self.diabetes_button_window = self.canvas.create_window(0, 0, window=self.diabetes_button, anchor="center")

        self.bind("<Configure>", self._resize_background)

        self.show_frame(HeartFrame)

    def _resize_background(self, event):
        resized = self.original_bg_img.resize((event.width, event.height), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(resized)

        self.canvas.delete("bg")
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw", tags="bg")
        self.canvas.tag_lower("bg")

        frame_width = int(event.width * 0.35)
        frame_height = int(event.height * 0.9)
        frame_x = int(event.width * 0.95)
        frame_y = int(event.height * 0.5)

        self.canvas.coords(self.main_window, frame_x, frame_y)
        self.main_frame.configure(width=frame_width, height=frame_height)

        center_x = event.width * 0.42
        center_y = event.height * 0.45
        spacing = 60

        self.canvas.coords(self.heart_button_window, center_x, center_y)
        self.canvas.coords(self.diabetes_button_window, center_x, center_y + spacing)

        new_font_size = max(10, int(event.width * 0.015))
        self.heart_button.config(font=("Arial", new_font_size, "bold"))
        self.diabetes_button.config(font=("Arial", new_font_size, "bold"))

    def show_frame(self, frame_class):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        frame_class(self.main_frame, self.logo_photo, self)



class HeartFrame(Frame):
    def __init__(self, parent, logo_photo, controller):
        super().__init__(parent, bg="white")

        # Initialize main_frame and logo_photo references
        self.main_frame = parent  # Assign main_frame from parent to the object
        self.logo_photo = logo_photo  # Assign logo_photo from parent to the object

        # Continue with the frame setup...
        self.controller = controller
        self.pack(fill="both", expand=True)

        def create_card(frame, title, value, unit, low, mid, high):
            card = Frame(frame, bg='#ffffff', bd=3, relief='solid', padx=10, pady=5)
            range_frame = Frame(card, bg='#ffffff')
            Label(range_frame, text=f"{low}", font=('Arial', 9), bg='#ffffff', fg='gray').pack(side="right")
            Label(range_frame, text=f" ⟷ ", font=('Arial', 9), bg='#ffffff', fg='gray').pack(side='left')
            Label(range_frame, text=f"{high}", font=('Arial', 9), bg='#ffffff', fg='gray').pack(side='left')
            range_frame.pack()

            Label(card, text=str(value), font=('Georgia', 22, 'bold'), bg='#ffffff', fg='#00796b').pack(pady=2)
            Label(card, text=title, font=('Arial', 11), bg='#ffffff').pack()
            Label(card, text=unit, font=('Arial', 9), bg='#ffffff', fg='gray').pack()
            return card

        def update_result(*args):
            try:
                s = int(systolic_slider.get())
                d = int(diastolic_slider.get())
                p = int(heart_rate_slider.get())
                weight = int(weight_slider.get())
            except ValueError:
                result_label.config(text="❌ Please select valid values.", fg="red")
                advice_label.config(text="")
                return

            if s < 90 or d < 60:
                status = "Low"
                color = "blue"
                advice_text = "⚠️ Low blood pressure. Stay hydrated and eat something salty."
            elif s < 120 and d < 80:
                status = "Normal"
                color = "green"
                advice_text = "✅ Your blood pressure is normal."
            elif 130 <= s < 140 or 85 <= d < 90:
                status = "Warning"
                color = "orange"
                advice_text = "⚠️ Warning: your pressure is approaching a critical level."
            elif 120 <= s <= 139 or 80 <= d <= 89:
                status = "Elevated"
                color = "yellow"
                advice_text = "⚠️ Elevated blood pressure. Consider lifestyle changes."
            
            elif s >= 140 or d >= 90:
                status = "High"
                color = "red"
                advice_text = "🚨 High blood pressure. Consult your doctor."
            else:
                status = "Unknown"
                color = "gray"
                advice_text = ""

            status_index = {'Low': 0, 'Normal': 1, 'Elevated': 2, 'Warning': 3, 'High': 4}.get(status, 0)
            pointer_x = status_index * 60 + 30

            result_label.config(text=f"Status: {status}", fg=color, font=("Arial", 24, "bold"))
            advice_label.config(text=advice_text, fg=color)

            for widget in card_frame.winfo_children():
                widget.destroy()

            create_card(card_frame, 'Systolic', s, 'mmHg', 90, 120, 140).grid(row=0, column=0, padx=10, pady=5)
            create_card(card_frame, 'Diastolic', d, 'mmHg', 60, 80, 90).grid(row=0, column=1, padx=5, pady=5)
            create_card(card_frame, 'Heart Rate', p, 'BPM', 50, 70, 100).grid(row=1, column=0, padx=5, pady=5)
            create_card(card_frame, 'Weight', weight, 'kg', 40, 70, 100).grid(row=1, column=1, padx=5, pady=5)

            bar.delete("all")
            colors = ['blue', 'green', 'yellow', 'orange', 'red']
            labels = ['Low', 'Normal', 'Elevated', 'Warning', 'High']

            for i, c in enumerate(colors):
                bar.create_rectangle(i * 60, 0, (i + 1) * 60, 30, fill=c, outline='black')
                bar.create_text((i * 60 + 30), 40, text=labels[i], fill='black', font=('Arial', 10))

            bar.create_text(pointer_x, 38, text='▲', fill='black', font=('Arial', 20, 'bold'))

        for widget in self.main_frame.winfo_children():
            widget.destroy()




        title_frame = Frame(self.main_frame, bg="white")
        title_frame.pack(fill="x", padx=10, pady=10)


        title_label = Label(title_frame, text=" Disease Measures", font=("Arial", 28, "bold"), bg="white", fg="#1976d2")
        title_label.pack(pady=10)

        canvas_frame = Frame(self.main_frame, bg="black")
        canvas_frame.pack(fill="both", expand=True)

        canvas = Canvas(canvas_frame, bg="white", width=450, height=450, highlightthickness=0)

        canvas.place(relx=0.95)
        scrollbar = Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg="white")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        Label(scrollable_frame, text="Systolic (mmHg):", font=("Georgia", 25), bg="white").pack(pady=0)
        systolic_slider = Scale(scrollable_frame, from_=-1, fg="black", to=300, orient=HORIZONTAL,
                                font=('Arial', 15, 'bold'), tickinterval=50, length=350, bg="sky blue")
        systolic_slider.pack(pady=2, padx=50)

        Label(scrollable_frame, text="Diastolic (mmHg):", font=("Georgia", 25), bg="white").pack(pady=5)
        diastolic_slider = Scale(scrollable_frame, from_=-1, fg="black", to=300, orient=HORIZONTAL,
                                 font=('Arial', 15, 'bold'), tickinterval=50, length=350, bg="sky blue")

        diastolic_slider.pack(pady=2)

        Label(scrollable_frame, text="Heart Rate (BPM):", font=("Georgia", 25), bg="white").pack(pady=5)
        heart_rate_slider = Scale(scrollable_frame, from_=-1, fg="black", to=200, orient=HORIZONTAL,
                                  font=('Arial', 15, 'bold'), tickinterval=40, length=350, bg="sky blue")
        heart_rate_slider.pack(pady=5)

        Label(scrollable_frame, text="Weight (kg):", font=("Georgia", 25), bg="white").pack(pady=5)
        weight_slider = Scale(scrollable_frame, from_=-1, fg="black", to=100, orient=HORIZONTAL,
                              font=('Arial', 15, 'bold'), tickinterval=20, length=350, bg="sky blue")
        weight_slider.pack(pady=5)

        global result_label, advice_label, card_frame, bar
        result_label = Label(scrollable_frame, text="Status: Pending...", font=("Arial", 16, "bold"), bg="white")
        result_label.pack(pady=10)

        advice_label = Label(scrollable_frame, text="", font=("Arial", 20, "bold"), fg="black", bg="white",
                             wraplength=320, justify="center")
        advice_label.pack()

        card_frame = Frame(scrollable_frame, bg='white')
        card_frame.pack(pady=10)

        bar = Canvas(scrollable_frame, width=300, height=60, bg='white', highlightthickness=0)
        bar.pack(pady=10)

        buttons_frame = Frame(scrollable_frame, bg="white")
        buttons_frame.pack(pady=15)

        style = ttk.Style()
        style.theme_use("default")

        style.configure("Save.TButton", background="#4682b4", foreground="white", font=("Arial", 14, 'bold'),
                        padding=10)
        style.map("Save.TButton", background=[("active", "#1976d2")], foreground=[("active", "white")])

        style.configure("Diabetes.TButton", background="#4682b4", foreground="white", font=("Arial", 14, 'bold'),
                        padding=10)
        style.map("Diabetes.TButton", background=[("active", "#1976d2")], foreground=[("active", "white")])

        save_button = ttk.Button(buttons_frame, text="💾Save Measurements", style="Save.TButton",
                                 command=lambda: save_measurements_to_db("Heart", {
                                     "Systolic": systolic_slider.get(),
                                     "Diastolic": diastolic_slider.get(),
                                     "Heart Rate": heart_rate_slider.get(),
                                     "Weight": weight_slider.get()
                                 }))
        save_button.pack(anchor="center", padx=10)

        

        for slider in [systolic_slider, diastolic_slider, heart_rate_slider, weight_slider]:
            slider.bind("<ButtonRelease-1>", update_result)

class DiabetesFrame(Frame):
    def __init__(self, parent, logo_photo, controller):
        super().__init__(parent, bg="white")

        self.main_frame = parent
        self.logo_photo = logo_photo  # Pass logo_photo to the frame correctly
        self.controller = controller
        self.pack(fill="both", expand=True)

        global diabetes_result_label, diabetes_advice_label, bar  # Declare globally to avoid issues

        def update_diabetes_result(*args):
            try:
                sugar = float(sugar_slider.get())
                time = time_var.get()
            except ValueError:
                diabetes_result_label.config(text="❌ Invalid input", fg="red")
                diabetes_advice_label.config(text="")
                return

            status = "Unknown"
            color = "gray"
            advice_text = ""
            if time == "Before Meal":
               if sugar < 4:
                status = "Low"
                color = "blue"
                advice_text = "⚠️ Blood sugar too low. Consider eating something sweet."
               elif 4 <= sugar <= 5.5:
                status = "Normal"
                color = "green"
                advice_text = "✅ Blood sugar is normal."
               elif 5.6 <= sugar <= 6.9:
                status = "Elevated"
                color = "yellow"
                advice_text = "⚠️ Elevated sugar level. Monitor regularly."
               elif 7 <= sugar <= 8:
                status = "Warning"
                color = "orange"
                advice_text = "⚠️ Warning! Blood sugar approaching high."
               else:
                status = "High"
                color = "red"
                advice_text = "🚨 High blood sugar. Consider insulin or doctor consultation."
            elif time == "2h After Meal":
                if sugar < 4:
                 status = "Low"
                 color = "blue"
                 advice_text = "⚠️ Blood sugar too low after eating. Consider a balanced snack."
                elif 4 <= sugar <= 7.8:
                 status = "Normal"
                 color = "green"
                 advice_text = "✅ Post-meal blood sugar is within normal range."
                elif 7.9 <= sugar <= 9:
                 status = "Elevated"
                 color = "yellow"
                 advice_text = "⚠️ Slightly elevated sugar. Monitor your diet and activity."
                elif 9.1 <= sugar <= 11:
                 status = "Warning"
                 color = "orange"
                 advice_text = "⚠️ Warning! Sugar approaching diabetic level. Reduce carbs, consult a doctor."
                else:
                 status = "High"
                 color = "red"
                 advice_text = "🚨 High blood sugar after meal. Consider medication and contact your doctor."
            elif time == "Random":
                if sugar < 4:
                 status = "Low"
                 color = "blue"
                 advice_text = "⚠️ Blood sugar too low. Eat something with carbs and monitor."
                elif 4 <= sugar <= 7.7:
                 status = "Normal"
                 color = "green"
                 advice_text = "✅ Blood sugar is in the normal range."
                elif 7.8 <= sugar <= 9:
                 status = "Elevated"
                 color = "yellow"
                 advice_text = "⚠️ Slightly high. Keep an eye on your sugar levels."
                elif 9.1 <= sugar <= 11:
                 status = "Warning"
                 color = "orange"
                 advice_text = "⚠️ Warning! Blood sugar nearing diabetic level. Reduce sugars, consult doctor."
                else:
                 status = "High"
                 color = "red"
                 advice_text = "🚨 Blood sugar too high. You may need medication — contact a professional."
            else:
                if sugar < 4:
                    status = "Low"
                    color = "blue"
                    advice_text = "⚠️ Blood sugar low. Take precautions."
                elif sugar <= 8:
                    status = "Normal"
                    color = "green"
                    advice_text = "✅ Blood sugar looks fine."
                else:
                    status = "High"
                    color = "red"
                    advice_text = "🚨 Blood sugar is high."

            diabetes_result_label.config(text=f"Status: {status}", fg=color, font=("Arial", 24, "bold"))
            diabetes_advice_label.config(text=advice_text, fg=color)

            # Update bar
            bar.delete("all")
            colors = ['blue', 'green', 'yellow', 'orange', 'red']
            labels = ['Low', 'Normal', 'Elevated', 'Warning', 'High']
            for i, c in enumerate(colors):
                bar.create_rectangle(i * 60, 0, (i + 1) * 60, 30, fill=c, outline='black')
                bar.create_text((i * 60 + 30), 40, text=labels[i], fill='black', font=('Arial', 10))

            status_index = {'Low': 0, 'Normal': 1, 'Elevated': 2, 'Warning': 3, 'High': 4}.get(status, 0)
            pointer_x = status_index * 60 + 30
            bar.create_text(pointer_x, 38, text='▲', fill='black', font=('Arial', 20, 'bold'))

        for widget in self.main_frame.winfo_children():
            widget.destroy()

        title_frame = Frame(self.main_frame, bg="white")
        title_frame.pack(fill="x", padx=10, pady=10)


        title_label = Label(title_frame, text="Diabetes Measures", font=("Arial", 28, "bold"), bg="white", fg="#1976d2")
        title_label.pack(pady=10)

        canvas_frame = Frame(self.main_frame, bg="black")
        canvas_frame.pack(fill="both", expand=True)

        canvas = Canvas(canvas_frame, bg="white", width=450, height=450, highlightthickness=0)
        canvas.place(relx=0.95)
        scrollbar = Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg="white")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Sliders and inputs
        style = ttk.Style()
        style.map('Custom.TCombobox', fieldbackground=[('readonly', 'white')], background=[('readonly', '#f8bbd0')])
        style.configure('Custom.TCombobox', padding=10, font=('Arial', 18), fieldbackground='white', background='white')
        style = ttk.Style()
        style.theme_use("default")
        style.configure('Custom.TCombobox',
                        padding=10,
                        font=('Arial', 18),
                        fieldbackground='#f8bbd0',
                        background='white',
                        selectbackground='white',
                        selectforeground='black',

                        )
        Label(scrollable_frame, text="Measurement Time:", font=("Georgia", 25, 'bold'), bg="white").pack(pady=5)
        time_var = StringVar()
        time_combobox = ttk.Combobox(
            scrollable_frame,
            textvariable=time_var,
            state="readonly",
            font=("Arial", 18),
            width=30,
            style="Custom.TCombobox"
        )
        time_combobox['values'] = ("Before Meal", "2h After Meal", "Random", "Before Sleep")
        time_combobox.current(0)
        time_combobox.pack(pady=5)

        Label(scrollable_frame, text="Blood Sugar Level (mmol/L):", font=("Georgia", 25), bg="white").pack(pady=5)
        sugar_slider = Scale(scrollable_frame,
                             from_=-1,
                             to=35,
                             resolution=0.1,
                             orient=HORIZONTAL,
                             font=('Arial', 15, 'bold'),
                             tickinterval=5,
                             length=350,
                             bg="#f8bbd0",
                             fg="black")
        sugar_slider.pack()


        sugar_slider.pack(pady=2, padx=50)

        Label(scrollable_frame, text="Insulin Dose (units):", font=("Georgia", 25), bg="white").pack(pady=5)
        insulin_slider   = Scale(scrollable_frame,
                             from_=-1,
                             to=50,
                             resolution=0.1,
                             orient=HORIZONTAL,
                             font=('Arial', 15, 'bold'),
                             tickinterval=10,
                             length=350,
                             bg="#f8bbd0",
                             fg="black")
        insulin_slider.pack(pady=5)

        Label(scrollable_frame, text="Carbs (grams):", font=("Georgia", 25), bg="white").pack(pady=5)
        carbs_slider = Scale(scrollable_frame, from_=-1, fg="black", to=300, orient=HORIZONTAL,
                             font=('Arial', 15, 'bold'), tickinterval=50, length=350, bg="#f8bbd0")
        carbs_slider.pack(pady=5)

        Label(scrollable_frame, text="Physical Activity (minutes):", font=("Georgia", 25), bg="white").pack(pady=5)
        activity_slider = Scale(scrollable_frame, from_=-1, fg="black", to=180, orient=HORIZONTAL,
                                font=('Arial', 15, 'bold'), tickinterval=30, length=350, bg="#f8bbd0")

        activity_slider.pack(pady=5)

        # Result and advice
        diabetes_result_label = Label(scrollable_frame, text="Status: Pending...", font=("Arial", 16, "bold"),
                                      bg="white")
        diabetes_result_label.pack(pady=10)

        diabetes_advice_label = Label(scrollable_frame, text="", font=("Arial", 18, "bold"), fg="black", bg="white",
                                      wraplength=320, justify="center")
        diabetes_advice_label.pack()

        # Always visible bar
        bar = Canvas(scrollable_frame, width=300, height=60, bg='white', highlightthickness=0)
        bar.pack(pady=10)

        colors = ['blue', 'green', 'yellow', 'orange', 'red']
        labels = ['Low', 'Normal', 'Elevated', 'Warning', 'High']
        for i, c in enumerate(colors):
            bar.create_rectangle(i * 60, 0, (i + 1) * 60, 30, fill=c, outline='black')
            bar.create_text((i * 60 + 30), 40, text=labels[i], fill='black', font=('Arial', 10))
        bar.create_text(30, 38, text='▲', fill='black', font=('Arial', 20, 'bold'))  # Default pointer

        # Buttons
        button_frame = Frame(scrollable_frame, bg="white")
        button_frame.pack(pady=15)

        

        save_button = ttk.Button(
            button_frame,
            text="💾 Save Measurment",
            style="Save.TButton",
            command=lambda: save_measurements_to_db("Diabetes", {
                "Blood Sugar": sugar_slider.get(),
                "Insulin": insulin_slider.get(),
                "Carbs": carbs_slider.get(),
                "Physical Activity": activity_slider.get()
            },time_var.get())
        )

        save_button.pack(anchor="center")

        # Bind sliders
        for slider in [sugar_slider, insulin_slider, carbs_slider, activity_slider]:
            slider.bind("<ButtonRelease-1>", update_diabetes_result)
