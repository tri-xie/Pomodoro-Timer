import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk


# Color Palette
BG_COLOR = "#2C3E50"      # Dark Slate Blue
TEXT_COLOR = "#ECF0F1"    # Off-White
WORK_COLOR = "#E74C3C"    # Tomato Red
BREAK_COLOR = "#2ECC71"   # Emerald Green

# Main application window (hidden while splash shows)
app = ctk.CTk()
app.title("Pomodoro : Keep Focused")
app.geometry("400x600")
app.resizable(False, False)
app.withdraw()

class SplashScreen:
    def __init__(self, master):
        self.master = master
        self.window = ctk.CTkToplevel(master)
        self.window.overrideredirect(True)
        self.window.config(bg=BG_COLOR)

        window_width = 450
        window_height = 300
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))
        self.window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        self.logo_label = tk.Label(
            self.window,
            text="🍅",
            font=("Helvetica", 70),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        self.logo_label.pack(expand=True, pady=(40, 0))

        self.title_label = tk.Label(
            self.window,
            text="POMODORO TIMER",
            fg=TEXT_COLOR,
            bg=BG_COLOR,
            font=("Helvetica", 24, "bold")
        )
        self.title_label.pack(expand=True)

        self.status_label = tk.Label(
            self.window,
            text="Loading engine.",
            fg=BREAK_COLOR,
            bg=BG_COLOR,
            font=("Helvetica", 12, "italic")
        )
        self.status_label.pack(expand=True, pady=(0, 40))

        self.animate_dots(0)
        self.window.after(3000, self.terminate_splash)

    def animate_dots(self, count):
        dots = "." * (count % 4)
        self.status_label.config(text=f"Loading engine{dots}")
        self.animation_id = self.window.after(400, self.animate_dots, count + 1)

    def terminate_splash(self):
        self.window.after_cancel(self.animation_id)
        self.window.destroy()
        launch_main_app()


def launch_main_app():
    app.deiconify()

    
SplashScreen(app)
app.mainloop()
