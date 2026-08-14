import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk

import config
from timer import PomodoroTimer

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Pomodoro : Keep Focused")
app.geometry("420x700")
app.minsize(420, 700)
# Allow the window to be resized and maximized
app.resizable(True, True)
app.iconbitmap(config.ICON_PATH)
logo_image = Image.open(config.LOGO_PATH)
logo_photo = ImageTk.PhotoImage(logo_image.resize((120, 120), Image.Resampling.LANCZOS), master=app)
app.withdraw()


class SplashScreen:
    def __init__(self, main):
        self.master = main
        self.window = ctk.CTkToplevel(main)
        self.window.overrideredirect(True)
        self.window.config(bg=config.BG_COLOR)

        window_width = 450
        window_height = 300
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))
        self.window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        self.logo_label = tk.Label(
            self.window,
            image=logo_photo,
            bg=config.BG_COLOR,
        )
        self.logo_label.image = logo_photo
        self.logo_label.pack(expand=True, pady=(40, 0))

        self.title_label = tk.Label(
            self.window,
            text="POMODORO TIMER",
            fg=config.TEXT_COLOR,
            bg=config.BG_COLOR,
            font=("Helvetica", 24, "bold"),
            justify="center",
        )
        self.title_label.pack(expand=True)

        self.subtitle_label = tk.Label(
            self.window,
            text="Keep Focused",
            fg=config.TEXT_COLOR,
            bg=config.BG_COLOR,
            font=("Helvetica", 14, "italic"),
            justify="center",
        )
        self.subtitle_label.pack(expand=True)

        self.status_label = tk.Label(
            self.window,
            text="Loading engine.",
            fg=config.BREAK_COLOR,
            bg=config.BG_COLOR,
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


def save_settings_and_close():
    if hasattr(app, "timer") and app.timer is not None:
        if hasattr(app.timer, "settings_panel") and app.timer.settings_panel is not None:
            app.timer.settings_panel._apply_changes()
        app.timer.save_settings()
    app.destroy()


def launch_main_app():
    app.deiconify()
    app.timer = PomodoroTimer(app)
    app.protocol("WM_DELETE_WINDOW", save_settings_and_close)


if __name__ == "__main__":
    SplashScreen(app)
    app.mainloop()
