import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk

icon_path = 'app logo.ico'
logo_path = 'app logo.jpg'  # Ensure the logo image is in the same directory or provide the correct path
logo_image = Image.open(logo_path)


# Color Palette
BG_COLOR = "#2C3E50"      # Dark Slate Blue
TEXT_COLOR = "#ECF0F1"    # Off-White
WORK_COLOR = "#E74C3C"    # Tomato Red
BREAK_COLOR = "#2ECC71"   # Emerald Green
INCLUDE_PAUSE_BUTTON = True  # Set to False if users do not want the Pause/Resume option

# Main application window (hidden while splash shows)
app = ctk.CTk()
app.title("Pomodoro : Keep Focused")
app.geometry("420x700")
app.minsize(420, 700)
app.resizable(False, False)
app.iconbitmap(icon_path)
logo_photo = ImageTk.PhotoImage(logo_image.resize((120, 120), Image.Resampling.LANCZOS), master=app)
app.withdraw()

class SplashScreen:
    def __init__(self, main):
        self.master = main
        self.window = ctk.CTkToplevel(main)
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
            image=logo_photo,
            bg=BG_COLOR,
        )
        self.logo_label.image = logo_photo  # Keep a reference to avoid garbage collection
        self.logo_label.pack(expand=True, pady=(40, 0))

        self.title_label = tk.Label(
            self.window,
            text="POMODORO TIMER",
            fg=TEXT_COLOR,
            bg=BG_COLOR,
            font=("Helvetica", 24, "bold"),
            justify="center",
        )
        self.title_label.pack(expand=True)

        self.subtitle_label = tk.Label(
            self.window,
            text="Keep Focused",
            fg=TEXT_COLOR,
            bg=BG_COLOR,
            font=("Helvetica", 14, "italic"),
            justify="center",
        )
        self.subtitle_label.pack(expand=True)

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
    PomodoroTimer(app)

WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20



class PomodoroTimer:
    def __init__(self, root, include_pause=INCLUDE_PAUSE_BUTTON):
        self.root = root
        self.include_pause = include_pause
        self.root.title("Pomodoro Timer")
        self.root.configure(padx=50, pady=25, bg="#f7f5dd")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_columnconfigure(2, weight=1)

        self.reps = 0
        self.timer_id = None
        self.is_running = False
        self.is_paused = False
        self.remaining_count = WORK_MIN * 60
        self.pause_button = None
        self.pause_option_var = tk.BooleanVar(value=self.include_pause)
        self.settings_panel_visible = False

        self.title_label = ctk.CTkLabel(
            self.root,
            text="Timer",
            text_color="#9bdeac",
            bg_color="#f7f5dd",
            font=("Courier", 35, "bold")
        )
        self.title_label.grid(column=1, row=0, pady=(10, 0))

        self.canvas = tk.Canvas(
            self.root,
            width=200,
            height=224,
            bg="#f7f5dd",
            highlightthickness=0
        )
        self.time_text = self.canvas.create_text(
            100, 112, text=f"{WORK_MIN:02d}:00", fill="#333333", font=("Courier", 35, "bold")
        )
        self.canvas.grid(column=1, row=1, pady=20)

        self.button_frame = ctk.CTkFrame(
            self.root,
            fg_color="#f7f5dd",
            corner_radius=0
        )
        self.button_frame.grid(column=0, row=2, columnspan=3, pady=(0, 10), sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        if self.include_pause:
            self.button_frame.grid_columnconfigure(2, weight=1)

        self.start_button = ctk.CTkButton(
            self.button_frame,
            text="Start",
            command=self.start_timer,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            width=120
        )
        self.start_button.grid(column=0, row=0, padx=(10, 5), pady=5, sticky="e")

        self.reset_button = ctk.CTkButton(
            self.button_frame,
            text="Reset",
            command=self.reset_timer,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=120
        )
        reset_column = 2 if self.include_pause else 1
        self.reset_button.grid(column=reset_column, row=0, padx=(5, 10), pady=5, sticky="w")

        if self.include_pause:
            self.create_pause_button()

        self.menu_button = ctk.CTkButton(
            self.root,
            text="☰",
            command=self.toggle_settings,
            fg_color="#ecf0f1",
            hover_color="#dfe6ea",
            text_color="#2c3e50",
            width=40,
            height=40,
            corner_radius=20,
        )
        self.menu_button.grid(column=0, row=0, padx=(10, 0), pady=(10, 0), sticky="w")

        self.settings_frame = ctk.CTkFrame(
            self.root,
            fg_color="#ecf0f1",
            corner_radius=10,
            border_width=1,
            border_color="#bdc3c7"
        )
        self.settings_frame.grid(column=0, row=4, columnspan=3, sticky="ew", padx=20, pady=(10, 0))
        self.settings_frame.grid_columnconfigure(0, weight=1)

        self.pause_option_checkbox = ctk.CTkCheckBox(
            self.settings_frame,
            text="Enable Pause",
            variable=self.pause_option_var,
            command=self.toggle_pause_option
        )
        self.pause_option_checkbox.grid(column=0, row=0, padx=10, pady=10, sticky="w")
        self.settings_frame.grid_remove()

        self.check_marks = ctk.CTkLabel(
            self.root,
            text="",
            text_color="#9bdeac",
            bg_color="#f7f5dd",
            font=("Courier", 18)
        )
        self.check_marks.grid(column=1, row=5, pady=(20, 0))

    def reset_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.reps = 0
        self.is_running = False
        self.is_paused = False
        self.remaining_count = WORK_MIN * 60
        self.canvas.itemconfig(self.time_text, text=f"{WORK_MIN:02d}:00")
        self.title_label.configure(text="Timer", text_color="#9bdeac")
        self.check_marks.configure(text="")
        self.start_button.configure(state="normal")
        if self.include_pause and self.pause_button:
            self.pause_button.configure(state="disabled", text="Pause")

    def create_pause_button(self):
        if self.pause_button:
            return
        self.button_frame.grid_columnconfigure(2, weight=1)
        self.pause_button = ctk.CTkButton(
            self.button_frame,
            text="Pause",
            command=self.toggle_pause,
            fg_color="#f39c12",
            hover_color="#d68910",
            width=120,
            state="disabled"
        )
        self.pause_button.grid(column=1, row=0, padx=5, pady=5)
        self.reset_button.grid_forget()
        self.reset_button.grid(column=2, row=0, padx=(5, 10), pady=5, sticky="w")

    def destroy_pause_button(self):
        if self.pause_button:
            self.pause_button.destroy()
            self.pause_button = None
        self.reset_button.grid_forget()
        self.reset_button.grid(column=1, row=0, padx=(5, 10), pady=5, sticky="w")

    def toggle_pause_option(self):
        self.include_pause = self.pause_option_var.get()
        if self.include_pause:
            self.create_pause_button()
        else:
            self.destroy_pause_button()

    def toggle_settings(self):
        if self.settings_panel_visible:
            self.settings_frame.grid_remove()
            self.menu_button.configure(fg_color="#ecf0f1")
        else:
            self.settings_frame.grid()
            self.menu_button.configure(fg_color="#ffffff")
        self.settings_panel_visible = not self.settings_panel_visible

    def start_timer(self):
        if self.is_running:
            return

        self.is_running = True
        self.is_paused = False
        self.start_button.configure(state="disabled")
        if self.include_pause and self.pause_button:
            self.pause_button.configure(state="normal", text="Pause")
        self.reps += 1

        if self.reps % 8 == 0:
            self.remaining_count = LONG_BREAK_MIN * 60
            self.title_label.configure(text="Long Break", text_color="#e7305b")
        elif self.reps % 2 == 0:
            self.remaining_count = SHORT_BREAK_MIN * 60
            self.title_label.configure(text="Short Break", text_color="#e2979c")
        else:
            self.remaining_count = WORK_MIN * 60
            self.title_label.configure(text="Work", text_color="#9bdeac")

        self.count_down(self.remaining_count)

    def toggle_pause(self):
        if self.is_paused:
            self.is_paused = False
            self.is_running = True
            self.pause_button.configure(text="Pause")
            self.count_down(self.remaining_count)
        else:
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None
            self.is_paused = True
            self.is_running = False
            self.pause_button.configure(text="Resume")
            self.start_button.configure(state="disabled")

    def count_down(self, count):
        self.remaining_count = count
        minutes = count // 60
        seconds = count % 60
        self.canvas.itemconfig(
            self.time_text, text=f"{minutes:02d}:{seconds:02d}"
        )

        if count > 0 and self.is_running:
            self.timer_id = self.root.after(1000, self.count_down, count - 1)
        elif count == 0:
            marks = "✔" * (self.reps // 2)
            self.check_marks.configure(text=marks)
            self.is_running = False
            if self.include_pause and self.pause_button:
                self.pause_button.configure(state="disabled", text="Pause")
            self.start_button.configure(state="normal")
    





if __name__ == "__main__":
    SplashScreen(app)
    app.mainloop()
