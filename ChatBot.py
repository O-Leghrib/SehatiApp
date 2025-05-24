import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import requests
import speech_recognition as sr

API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"

SYSTEM_PROMPT = (
    "You are a health assistant focused on diabetes and high blood pressure. "
    "Only answer questions related to these conditions in a calm, supportive, and helpful tone.\n"
    "If the user asks something unrelated to diabetes or high blood pressure, kindly respond: "
    "\"I’m here to help with diabetes and high blood pressure. Let’s focus on that together.\""
)

SUGGESTIONS = [
    "How to manage high blood pressure?",
    "What are healthy foods for diabetes?",
    "Can I exercise with hypertension?",
    "What are signs of high blood sugar?",
]

class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)
        self._add_placeholder()

    def _clear_placeholder(self, event=None):
        if self.get() == self.placeholder and self['fg'] == self.placeholder_color:
            self.delete(0, tk.END)
            self['fg'] = self.default_fg_color

    def _add_placeholder(self, event=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self['fg'] = self.placeholder_color

class ChatbotFrame(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        self.left_frame = tk.Frame(self, width=300, bg="#f0f0f0")
        self.left_frame.pack(side="left", fill="y")

        self.right_frame = tk.Frame(self, bg="white")
        self.right_frame.pack(side="right", fill="both", expand=True)

        left_width = 300  # Set this to match the width of self.left_frame
        img = Image.open("images/bgChatBot.png")
        img = img.resize((570, 550), Image.Resampling.LANCZOS)
        self.bot_photo = ImageTk.PhotoImage(img)
        self.image_label = tk.Label(self.left_frame, image=self.bot_photo, bg="#f0f0f0")
        self.image_label.pack(pady=8)

        self.suggestion_frame = tk.Frame(self.left_frame, bg="#f0f0f0")
        self.suggestion_frame.pack(fill="x", padx=10, pady=(0,20))
        for prompt in SUGGESTIONS:
            btn = tk.Button(
                self.suggestion_frame,
                text=prompt, wraplength=160, bg="#c3aed6", fg="white",
                relief=tk.FLAT, font=("Arial", 13, "bold"),
                height=3, command=lambda p=prompt: self.send_message(p)
            )
            btn.pack(side="left", padx=3, pady=3, expand=True, fill="x")
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
        self.chat_frame = tk.Frame(self.right_frame, bg="white")
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=(10,0))
        self.canvas = tk.Canvas(self.chat_frame, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.chat_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.messages_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0,0), window=self.messages_frame, anchor="nw")
        self.messages_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.entry_frame = tk.Frame(self.right_frame, bg="white")
        self.entry_frame.pack(fill="x", padx=10, pady=10)
        self.entry = PlaceholderEntry(
            self.entry_frame, placeholder="Ask about diabetes or blood pressure",
            font=("Arial", 12), bg="white", fg="black", bd=1, relief="solid"
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.entry.bind("<Return>", lambda e: self.send_message())

        self.send_button = tk.Button(
            self.entry_frame, text="➤", font=("Arial", 14, "bold"),
            bg="#4a90e2", fg="white", command=self.send_message,
            relief="flat", cursor="hand2", width=3
        )
        self.send_button.pack(side="left", padx=(0,5))

        self.mic_button = tk.Button(
            self.entry_frame, text="🎤", font=("Arial", 14),
            bg="#e94e77", fg="white", command=self.listen_voice,
            relief="flat", cursor="hand2", width=3
        )
        self.mic_button.pack(side="left")

        self.update_messages()

    def update_messages(self):
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        for msg in self.messages:
            if msg["role"] == "system":
                continue
            text = msg["content"]
            role = msg["role"]
            bg_color = "#48bfe3"
            fg_color = "white"
            anchor = "e" if role == "user" else "w"
            justify = "right" if role == "user" else "left"
            padx = (150, 10) if role == "user" else (10, 150)
            frame = tk.Frame(self.messages_frame, bg=bg_color, padx=10, pady=6)
            frame.pack(anchor=anchor, pady=5, padx=padx, fill="none")
            label = tk.Label(
                frame, text=text, bg=bg_color, fg=fg_color,
                font=("Arial", 12), wraplength=400, justify=justify
            )
            label.pack()
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(1)

    def send_message(self, preset=None):
        user_input = preset or self.entry.get().strip()
        if not user_input or user_input == self.entry.placeholder:
            return
        self.entry.delete(0, tk.END)
        self.entry._add_placeholder()
        self.messages.append({"role": "user", "content": user_input})
        self.update_messages()
        self.messages.append({"role": "assistant", "content": "Bot is typing..."})
        self.update_messages()
        threading.Thread(target=self.get_response, daemon=True).start()

    def remove_typing(self):
        if self.messages and self.messages[-1]["content"] == "Bot is typing...":
            self.messages.pop()

    def get_response(self):
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        body = {"model": "mistralai/mistral-7b-instruct", "messages": self.messages}
        try:
            response = requests.post(API_URL, headers=headers, json=body)
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
            else:
                content = f"⚠️ Request failed: {response.status_code}"
        except Exception as e:
            content = f"⚠️ Error: {e}"
        self.after(0, self.show_bot_reply, content)

    def show_bot_reply(self, message):
        self.remove_typing()
        self.messages.append({"role": "assistant", "content": message})
        self.update_messages()

    def listen_voice(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                self.entry.delete(0, tk.END)
                self.entry.insert(0, "Listening...")
                audio = r.listen(source, timeout=5)
                text = r.recognize_google(audio) 
                self.entry.delete(0, tk.END)
                self.entry.insert(0, text)
                self.send_message()
            except Exception:
                self.entry.delete(0, tk.END)
                self.entry.insert(0, "Speech not recognized")
