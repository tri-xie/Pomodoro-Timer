import tkinter as tk
import tkinter.font as tkfont
import customtkinter as ctk

import config
from settings import SettingsPanel


class PomodoroTimer:
    def __init__(self, root, include_pause=config.INCLUDE_PAUSE_BUTTON):
        self.root = root
        user_settings = config.load_user_settings()
        self.include_pause = user_settings.get("include_pause", include_pause)
        self.theme = user_settings.get("theme", config.DEFAULT_THEME)
        self.palette = config.THEME_PALETTES.get(self.theme, config.THEME_PALETTES[config.DEFAULT_THEME])
        self.root.title("Pomodoro Timer")
        self.root.configure(padx=20, pady=20, bg=self.palette["APP_BG"])
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=0)

        self.reps = 0
        self.timer_id = None
        self.is_running = False
        self.is_paused = False
        self.work_min = user_settings.get("work_min", config.WORK_MIN)
        self.short_break_min = user_settings.get("short_break_min", config.SHORT_BREAK_MIN)
        self.long_break_min = user_settings.get("long_break_min", config.LONG_BREAK_MIN)
        self.remaining_count = self.work_min * 60
        self.pause_button = None
        self.pause_option_var = tk.BooleanVar(value=self.include_pause)
        self.settings_panel = None

        self.title_label = ctk.CTkLabel(
            self.root,
            text="Timer",
            text_color=self.palette["TEXT_COLOR"],
            bg_color=self.palette["APP_BG"],
            font=("Courier", 35, "bold")
        )
        self.title_label.grid(column=1, row=0, pady=(10, 0))

        self.canvas = tk.Canvas(
            self.root,
            width=200,
            height=224,
            bg=self.palette["CANVAS_BG"],
            highlightthickness=0
        )
        self.time_font = tkfont.Font(family="Courier", size=35, weight="bold")
        self.time_text = self.canvas.create_text(
            100, 112, text=f"{self.work_min:02d}:00", fill=self.palette["TEXT_COLOR"], font=self.time_font
        )
        self.canvas.grid(column=1, row=1, pady=20)

        self.button_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.palette["APP_BG"],
            corner_radius=0
        )
        self.button_frame.grid(column=1, row=2, pady=(0, 10), sticky="ew")
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
        )
        self.start_button.grid(column=0, row=0, padx=(10, 5), pady=5, sticky="ew")

        self.reset_button = ctk.CTkButton(
            self.button_frame,
            text="Reset",
            command=self.reset_timer,
            fg_color="#e74c3c",
            hover_color="#c0392b",
        )
        reset_column = 2 if self.include_pause else 1
        self.reset_button.grid(column=reset_column, row=0, padx=(5, 10), pady=5, sticky="ew")

        if self.include_pause:
            self.create_pause_button()

        self.menu_button = ctk.CTkButton(
            self.root,
            text="⚙ Settings",
            command=self.toggle_settings_panel,
            fg_color=self.palette["BUTTON_BG"],
            hover_color=self.palette["BUTTON_BG"],
            text_color=self.palette["TEXT_COLOR"],
            width=110,
            height=40,
            corner_radius=20,
        )
        self.menu_button.grid(column=0, row=0, padx=(10, 0), pady=(10, 0), sticky="w")

        self.settings_panel = SettingsPanel(self.root, self)

        self.check_marks = ctk.CTkLabel(
            self.root,
            text="",
            text_color="#9bdeac",
            bg_color=self.palette["APP_BG"],
            font=("Courier", 18)
        )
        self.check_marks.grid(column=1, row=5, pady=(20, 0))
        self.apply_theme()

    def reset_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.reps = 0
        self.is_running = False
        self.is_paused = False
        self.remaining_count = self.work_min * 60
        self.canvas.itemconfig(self.time_text, text=f"{self.work_min:02d}:00")
        self.title_label.configure(text="Timer", text_color=self.palette["TEXT_COLOR"])
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
            state="disabled"
        )
        self.pause_button.grid(column=1, row=0, padx=5, pady=5, sticky="ew")
        self.reset_button.grid_forget()
        self.reset_button.grid(column=2, row=0, padx=(5, 10), pady=5, sticky="w")

    def destroy_pause_button(self):
        if self.pause_button:
            self.pause_button.destroy()
            self.pause_button = None
        self.reset_button.grid_forget()
        self.reset_button.grid(column=1, row=0, padx=(5, 10), pady=5, sticky="ew")

    def toggle_pause_option(self):
        self.include_pause = self.pause_option_var.get()
        if self.include_pause:
            self.create_pause_button()
        else:
            self.destroy_pause_button()

    def toggle_settings_panel(self):
        self.settings_panel.toggle()

    def apply_theme(self):
        self.palette = config.THEME_PALETTES[self.theme]
        ctk.set_appearance_mode(self.theme)
        self.root.configure(bg=self.palette["APP_BG"])
        self.title_label.configure(bg_color=self.palette["APP_BG"], text_color=self.palette["TEXT_COLOR"])
        self.canvas.configure(bg=self.palette["CANVAS_BG"])
        self.canvas.itemconfig(self.time_text, fill=self.palette["TEXT_COLOR"])
        self.button_frame.configure(fg_color=self.palette["APP_BG"])
        self.check_marks.configure(bg_color=self.palette["APP_BG"], text_color=self.palette["TEXT_COLOR"])
        self.settings_panel.refresh_theme()

    def save_settings(self):
        config.save_user_settings({
            "theme": self.theme,
            "work_min": self.work_min,
            "short_break_min": self.short_break_min,
            "long_break_min": self.long_break_min,
            "include_pause": self.include_pause,
        })

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
            self.remaining_count = self.long_break_min * 60
            self.title_label.configure(text="Long Break", text_color="#e7305b")
        elif self.reps % 2 == 0:
            self.remaining_count = self.short_break_min * 60
            self.title_label.configure(text="Short Break", text_color="#e2979c")
        else:
            self.remaining_count = self.work_min * 60
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


