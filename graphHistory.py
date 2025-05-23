from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import matplotlib.dates as mdates

class HistoryPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg="white")

        try:
            icon_image = Image.open("images/icn.png")
            icon = ImageTk.PhotoImage(icon_image)
            self.controller.iconphoto(True, icon)
        except FileNotFoundError:
            print("Error: 'icn.png' not found.")
        except Exception as e:
            print(f"Error loading 'icn.png': {e}")

        
        # Create and pack background canvas
        self.background_canvas = Canvas(self, highlightthickness=0)
        self.background_canvas.pack(fill=BOTH, expand=True)
       


        # Load and display background image
        self.original_bg = Image.open("images/bgGraphHistory.png")
        self.background_image = ImageTk.PhotoImage(self.original_bg)
        self.background = self.background_canvas.create_image(0, 0, anchor="nw", image=self.background_image)
        self.background_canvas.tag_lower(self.background)
        self.bind("<Configure>", self.resize_background)

        # Home button
        homeb = Button(self, text="🏠 Home", background="#48bfe3", foreground="#ffffff",
                       command=lambda: controller.show_frame("homepage"),
                       font=("Arial", 14, "bold"), width=11)
        homeb.place(x=10, y=10)

        # Title
        Label(self, text="📊Evolution", font=("wide latin", 35, "bold"), fg="#b19cd9", bg="white").place(x=200, y=100)

        # Graph frame
        self.graph_frame = Frame(self, bg="white", highlightbackground="#e0aaff", highlightthickness=3, bd=0)
        self.graph_frame.place(x=80, y=180, width=700, height=450)

        # Dropdown frame
        self.dropdown_frame = Frame(self, bg="#f3e8ff")
        self.dropdown_frame.place(x=800, y=300)

        # Disease buttons
        Button(self, text="Diabetes",
               command=lambda: self.show_dropdown(
                   ["Diabetes:Blood Sugar", "Diabetes:Insulin", "Diabetes:Carbs", "Diabetes:Physical Activity"],
                   "Select a Diabetes measurement:", is_diabetes=True),
               font=("MV Boli", 13, "bold"), bg="#b19cd9", fg="white",
               activebackground="#9085eb", width=20).place(x=825, y=200)

        Button(self, text="Heart Disease",
               command=lambda: self.show_dropdown(
                   ["Heart:Systolic", "Heart:Diastolic", "Heart:Heart Rate", "Heart:Weight"],
                   "Select a Heart Disease measurement:", is_diabetes=False),
               font=("MV Boli", 13, "bold"), bg="#b19cd9", fg="white",
               activebackground="#9085eb", width=20).place(x=825, y=260)

        # Ensure dropdown frame is placed last
        self.dropdown_frame = Frame(self, bg="#f3e8ff")
        self.dropdown_frame.place(x=810, y=320)

    def resize_background(self, event=None):
        width = self.winfo_width()
        height = self.winfo_height()

        if width > 0 and height > 0:
            resized_bg = self.original_bg.resize((width, height), Image.LANCZOS)
            self.background_image = ImageTk.PhotoImage(resized_bg)
            self.background_canvas.itemconfig(self.background, image=self.background_image)
            self.background_canvas.coords(self.background, 0, 0)

    def draw_graph(self, measure_type, time_context="All"):
        base_type = measure_type.split(":")[1].strip()

        conn = sqlite3.connect("basededon.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, value, measure_type 
            FROM measurements 
            WHERE measure_type LIKE ?
            ORDER BY date ASC
        """, (f"%:{base_type}%",))
        data = cursor.fetchall()
        conn.close()

        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        if not data:
            print(f"No data found for: {measure_type}")
            return

        grouped = {}
        for date_str, value, full_type in data:
            parts = full_type.split(":")
            context = parts[2].strip() if len(parts) > 2 else "None"

            if "Diabetes" in measure_type and time_context != "All" and context != time_context:
                continue

            date = datetime.strptime(date_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
            grouped.setdefault(context, []).append((date, value))

        fig, ax = plt.subplots(figsize=(7, 4))

        if not grouped:
            ax.text(0.5, 0.5, f"No data for {measure_type} - {time_context}", fontsize=12, ha='center')
        else:
            color_map = {
                "Before Meal": "green",
                "2h After Meal": "blue",
                "Random": "orange",
                "Before Sleep": "red",
                "None": "gray"
            }

            for context, values in grouped.items():
                values.sort()
                dates, vals = zip(*values)
                label = context if "Diabetes" in measure_type else base_type
                ax.plot(dates, vals, marker='o', linestyle='-', label=label, color=color_map.get(context, "black"))

        ax.set_xlabel("Date and Time")
        ax.set_ylabel("Value")
        ax.set_title(f"{base_type} ({time_context if 'Diabetes' in measure_type else 'All'})")
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        ax.tick_params(axis='x', rotation=60)
        fig.autofmt_xdate()
        ax.legend(title="Time Context", loc='upper right')

        scroll_canvas = Canvas(self.graph_frame, bg="white", highlightthickness=0)
        scroll_canvas.pack(fill=BOTH, expand=True)

        inner_frame = Frame(scroll_canvas, bg="white")
        scroll_canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        canvas = FigureCanvasTkAgg(fig, master=inner_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

        inner_frame.update_idletasks()
        scroll_canvas.config(scrollregion=scroll_canvas.bbox("all"))

        styled_scrollbar = ttk.Scrollbar(self.graph_frame, orient=HORIZONTAL, command=scroll_canvas.xview)
        scroll_canvas.configure(xscrollcommand=styled_scrollbar.set)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Horizontal.TScrollbar",
                        troughcolor="#ffe4ec",
                        background="#cdb4db",
                        bordercolor="#ffffff",
                        arrowcolor="#6a0572",
                        relief="flat")
        styled_scrollbar.pack(fill=X)

    def show_dropdown(self, options, label_text, is_diabetes=False):
        for widget in self.dropdown_frame.winfo_children():
            widget.destroy()

        selected = StringVar()
        selected.set("Choose...")

        label = Label(self.dropdown_frame, text=label_text,
                      font=("Arial", 12), bg="#f3e8ff", fg="#6a0572")
        label.pack(pady=(5, 0))

        dropdown = ttk.Combobox(self.dropdown_frame, textvariable=selected, values=options,
                                font=("Arial", 11), state="readonly")
        dropdown.pack(pady=5)

        if is_diabetes:
            time_filter_label = Label(self.dropdown_frame, text="Time Context:",
                                      font=("Arial", 11), bg="#f3e8ff", fg="#6a0572")
            time_filter_label.pack(pady=(10, 0))

            time_filter_var = StringVar()
            time_filter = ttk.Combobox(self.dropdown_frame, textvariable=time_filter_var,
                                       values=["All", "Before Meal", "2h After Meal", "Random", "Before Sleep"],
                                       font=("Arial", 11), state="readonly")
            time_filter.set("All")
            time_filter.pack()

            def update_graph(event=None):
                self.draw_graph(selected.get(), time_filter_var.get())

            dropdown.bind("<<ComboboxSelected>>", update_graph)
            time_filter.bind("<<ComboboxSelected>>", update_graph)

        else:
            def update_graph(event=None):
                self.draw_graph(selected.get(), "All")

            dropdown.bind("<<ComboboxSelected>>", update_graph)
