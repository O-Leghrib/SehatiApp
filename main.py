import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import time
import os # Added for path handling and file checks
import bcrypt # Added for login authentication in LogSignPage

# Import your page classes
# Make sure these filenames match your actual file names (e.g., HomePage.py)
from HomePage import homepage 
from LOGIN import LogSign
from SIGNUP import SignUpPage
from form import SihatiForm
from userSettings import UserPage
from graphHistory import HistoryPage
from remindershistory import ReminderHistoryApp
from enterReminders import ReminderFrame
from enterMeasure import SehatiApp
from ChatBot import ChatbotFrame

from db_operations import initialize_database_unified 

def show_splash():
    splash = tk.Tk()
    splash.overrideredirect(True)  
    splash.configure(bg="#d0eaff")
    
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()

  
    width = int(screen_width * 0.7) 
    height = int(screen_height * 0.7) 
    x = (screen_width - width) // 2  
    y = (screen_height - height) // 2
    splash.geometry(f"{width}x{height}+{x}+{y}")  

    
    icon_path = "images/SehatiApp_icon2.png"  
    try:
        # Check if the icon file exists before opening
        if os.path.exists(icon_path):
            img = Image.open(icon_path)
            img = img.resize((300, 300), Image.LANCZOS)
            logo = ImageTk.PhotoImage(img)
            label_img = tk.Label(splash, image=logo, bg="#d0eaff")
            label_img.image = logo
            label_img.pack(pady=20)
        else:
            print(f"Warning: Icon file not found at {icon_path}. Skipping icon display.")
            # Fallback for missing icon: just show the text
            tk.Label(splash, text="Loading...", font=("Arial", 30), bg="#d0eaff", fg="#003366").pack(pady=20)
            
    except Exception as e:
        print(f"Error loading image: {e}") 

    # ظل للنص (This part might be for visual effect, keep as is if intended)
    # النص الرئيسي فوقه
    main_label = tk.Label(
        splash,
        text="SEHATI",
        font=("Arial", 70, "bold"),
        bg="#d0eaff",
        fg="#003366"  # لون النص الحقيقي
    )
    main_label.place(relx=0.5, rely=0.75, anchor="center")
    
    splash.after(3000, splash.destroy)  # يغلق بعد 3 ثوانٍ
    splash.mainloop()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sehati")
        self.state('zoomed')

        initialize_database_unified() 
        print("App.__init__: Database initialized.")

       
        self.current_user_id = None 
        print(f"App.__init__: Initializing current_user_id = {self.current_user_id}")
        

        self.frames = {}
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        
        self.frames["homepage"] = homepage(container, self)
        self.frames["LogSign"] = LogSign(container, self)
        self.frames["SignUpPage"] = SignUpPage(container, self)
        self.frames["SihatiForm"] = SihatiForm(container, self, user_id=self.current_user_id) # Pass user_id here
        self.frames["UserPage"] = UserPage(container, self)
        self.frames["HistoryPage"] = HistoryPage(container, self)
        self.frames["ReminderHistoryApp"] = ReminderHistoryApp(container, self)
        self.frames["ReminderFrame"] = ReminderFrame(container, self)
        self.frames["SehatiApp"] = SehatiApp(container, self)
        self.frames["ChatbotFrame"] = ChatbotFrame(container, self)   
        
        for name, frame_instance in self.frames.items():
            frame_instance.grid(row=0, column=0, sticky="nsew")
            print(f"App.__init__: Frame '{name}' initialized.")


        self.show_frame("LogSign")

    def show_frame(self, frame_name):
        print(f"\nApp.show_frame: Request to show page '{frame_name}'")
        print(f"App.show_frame: Controller's current_user_id before frame logic = {self.current_user_id}")
        
        frame = self.frames.get(frame_name)
        if not frame:
            messagebox.showerror("Error", f"Page '{frame_name}' not found in frames dictionary.")
            return

        
        if frame_name == "SihatiForm":
            if self.current_user_id is None:
                messagebox.showwarning("Access Denied", "Please log in or sign up to access the health form.")
                self.show_frame("LogSign") # Redirect to login if no user is set
                print("App.show_frame: Redirected to LogSign because current_user_id is None.")
                return
            

            print(f"App.show_frame: Updating SihatiForm's user_id to {self.current_user_id}")
            frame.user_id = self.current_user_id # <--- SETTING THE USER_ID ON THE FRAME
            frame.load_existing_data()           # <--- CALLING LOAD DATA METHOD
            print(f"App.show_frame: Called load_existing_data on SihatiForm for user_id {frame.user_id}")

       
        frame.tkraise()
        print(f"App.show_frame: Frame '{frame_name}' raised.")

    
    def set_current_user_id(self, user_id):
        """Method to set the current logged-in user's ID."""
        self.current_user_id = user_id
        print(f"App.set_current_user_id: Controller's current_user_id updated to {self.current_user_id}")


if __name__ == "__main__":
    show_splash() 
    app = App()  
    app.mainloop()