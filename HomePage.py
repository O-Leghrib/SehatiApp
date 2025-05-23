import tkinter as tk
from PIL import Image, ImageTk

class homepage(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller
        try:
            self.original_image = Image.open("images/bgHome.png")
        except FileNotFoundError:
            print("ERROR: 'bgHome.png' not found. Check the path.")
            self.original_image = Image.new("RGB", (800, 600), "gray")  # fallback image
       
        self.bg_image = None

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.bg_image_id = self.canvas.create_image(0, 0, anchor="nw")
        self.title = self.canvas.create_text(0, 0, text=" ",
                                             font=("Pacifico", 40, "bold"), fill="purple")

        # زر إظهار القائمة الجانبية
        self.toggle_btn = tk.Button(self, text="☰", command=self.toggle_sidebar,
                                    bg="deepskyblue", fg="white", font=("Arial", 14), width=3)
        self.toggle_btn_id = self.canvas.create_window(10, 10, anchor="nw", window=self.toggle_btn)

        # أزرار منتصف الشاشة
        self.btn1 = tk.Button(self, text="Enter Measures", command=lambda:controller.show_frame("SehatiApp"),
                              bg="deepskyblue", fg="white", font=("Arial", 14, "bold"), width=20, height=2)
        self.btn2 = tk.Button(self, text="Enter Reminders", command=lambda:controller.show_frame("ReminderFrame"),
                              bg="deepskyblue", fg="white", font=("Arial", 14, "bold"), width=20, height=2)
        self.btn1_id = self.canvas.create_window(0, 0, window=self.btn1)
        self.btn2_id = self.canvas.create_window(0, 0, window=self.btn2)

        # أزرار أسفل الشاشة
        self.bottom_btn1 = tk.Button(self, text="Reminders History", command=lambda:controller.show_frame("ReminderHistoryApp"),
                                     bg="deepskyblue", fg="white", font=("Arial", 14, "bold"), width=20, height=2)
        self.bottom_btn2 = tk.Button(self, text="Historique", command=lambda:controller.show_frame("HistoryPage"),
                                     bg="deepskyblue", fg="white", font=("Arial", 14, "bold"), width=20, height=2)
        self.bottom_btn1_id = self.canvas.create_window(0, 0, window=self.bottom_btn1)
        self.bottom_btn2_id = self.canvas.create_window(0, 0, window=self.bottom_btn2)

        # القائمة الجانبية
        self.sidebar_width = 150
        self.sidebar = tk.Frame(self, bg="white", width=self.sidebar_width, height=500)
        self.sidebar.place(x=-self.sidebar_width, y=0)  # مخفية بالبداية
        self.sidebar_visible = False
        self.sidebar_animating = False

        # زر إغلاق القائمة
        close_btn = tk.Button(self.sidebar, text="⬅", command=self.toggle_sidebar,
                              bg="black", fg="white", font=("Arial", 12))
        close_btn.pack(fill="x", pady=2)

        # أزرار القائمة
        
        btn1 = tk.Button(self.sidebar, text="User Settings", bg="deepskyblue", fg="white", font=("Arial", 12),
                         command=lambda:controller.show_frame("UserPage"))
        btn1.pack(fill="x", pady=2)
        btn2 = tk.Button(self.sidebar, text="Log Out", bg="deepskyblue", fg="white", font=("Arial", 12),
                         command=lambda:controller.show_frame("LogSign"))
        btn2.pack(fill="x", pady=2)

        self.after(100, self.resize_background)
        self.bind("<Configure>", self.resize_background)
        self.canvas.bind("<Button-1>", self.on_click_outside_sidebar)


    def toggle_sidebar(self):
        if self.sidebar_animating:
            return
        if self.sidebar_visible:
            self.slide_out()
        else:
            self.slide_in()

    def slide_in(self):
        self.sidebar_animating = True
        def step(pos):
            if pos >= 0:
                self.sidebar.place(x=0, y=0, height=self.winfo_height())
                self.sidebar_visible = True
                self.sidebar_animating = False
                return
            self.sidebar.place(x=pos, y=0, height=self.winfo_height())
            self.after(10, lambda: step(pos + 15))  # السرعة
        step(-self.sidebar_width)

    def slide_out(self):
        self.sidebar_animating = True
        def step(pos):
            if pos <= -self.sidebar_width:
                self.sidebar.place(x=-self.sidebar_width, y=0)
                self.sidebar_visible = False
                self.sidebar_animating = False
                return
            self.sidebar.place(x=pos, y=0, height=self.winfo_height())
            self.after(10, lambda: step(pos - 15))  # السرعة
        step(0)
    def resize_background(self, event=None):
        width = self.winfo_width()
        height = self.winfo_height()

        if width < 2 or height < 2:
            return

        resized = self.original_image.resize((width, height), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(resized)

        self.canvas.config(width=width, height=height)
        self.canvas.itemconfig(self.bg_image_id, image=self.bg_image)
        self.canvas.coords(self.bg_image_id, 0, 0)

        self.canvas.coords(self.title, width // 2, height // 8)
        self.canvas.coords(self.btn1_id, width // 2, height // 2 - 90)
        self.canvas.coords(self.btn2_id, width // 2, height // 2 - 20)
        self.canvas.coords(self.bottom_btn1_id, width // 2 - 150, height - 50)
        self.canvas.coords(self.bottom_btn2_id, width // 2 + 150, height - 50)

        if self.sidebar_visible:
            self.sidebar.place(x=0, y=0, height=height)
    def on_click_outside_sidebar(self, event):
        if self.sidebar_visible:
            x, y = event.x, event.y
        # نحصل على حدود القائمة الجانبية
            sidebar_x = self.sidebar.winfo_x()
            sidebar_y = self.sidebar.winfo_y()
            sidebar_width = self.sidebar.winfo_width()
            sidebar_height = self.sidebar.winfo_height()

        # إذا كانت النقرة خارج حدود القائمة
            if not (sidebar_x <= x <= sidebar_x + sidebar_width and sidebar_y <= y <= sidebar_y + sidebar_height):
                self.slide_out()


#
