import tkinter as tk
import customtkinter as ctk

import config


class SettingsPanel:
    def __init__(self, parent, timer):
        self.parent = parent
        self.timer = timer
        self.visible = False

        self.frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="#ecf0f1",
            corner_radius=10,
            border_width=1,
            border_color="#bdc3c7",
            height=320
        )
        self.frame.grid_columnconfigure(0, weight=1)

        self.pause_option_var = tk.BooleanVar(value=self.timer.include_pause)
        self.skip_option_var = tk.BooleanVar(value=self.timer.include_skip)
        self.work_min_var = tk.StringVar(value=str(self.timer.work_min))
        self.short_break_min_var = tk.StringVar(value=str(self.timer.short_break_min))
        self.long_break_min_var = tk.StringVar(value=str(self.timer.long_break_min))
        self.work_message_var = tk.StringVar(value=self.timer.work_message)
        self.short_break_message_var = tk.StringVar(value=self.timer.short_break_message)
        self.long_break_message_var = tk.StringVar(value=self.timer.long_break_message)
        self.app_font_var = tk.StringVar(value=self.timer.app_font_family)
        self.message_font_var = tk.StringVar(value=self.timer.message_font_family)
        self.theme_var = tk.StringVar(value=self.timer.theme)
        self.updating = False

        self.pause_checkbox = ctk.CTkCheckBox(
            self.frame,
            text="Enable Pause",
            variable=self.pause_option_var,
            command=self._apply_changes
        )
        self.pause_checkbox.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.skip_checkbox = ctk.CTkCheckBox(
            self.frame,
            text="Enable Skip",
            variable=self.skip_option_var,
            command=self._apply_skip_option_change
        )
        self.skip_checkbox.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        self.work_label = ctk.CTkLabel(self.frame, text="Work duration (minutes):")
        self.work_label.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")
        self.work_entry = ctk.CTkEntry(self.frame, textvariable=self.work_min_var, width=120)
        self.work_entry.grid(row=3, column=0, padx=20, pady=(5, 10), sticky="w")

        self.short_break_label = ctk.CTkLabel(self.frame, text="Short break (minutes):")
        self.short_break_label.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")
        self.short_break_entry = ctk.CTkEntry(self.frame, textvariable=self.short_break_min_var, width=120)
        self.short_break_entry.grid(row=5, column=0, padx=20, pady=(5, 10), sticky="w")

        self.long_break_label = ctk.CTkLabel(self.frame, text="Long break (minutes):")
        self.long_break_label.grid(row=6, column=0, padx=20, pady=(10, 0), sticky="w")
        self.long_break_entry = ctk.CTkEntry(self.frame, textvariable=self.long_break_min_var, width=120)
        self.long_break_entry.grid(row=7, column=0, padx=20, pady=(5, 10), sticky="w")

        self.work_message_label = ctk.CTkLabel(self.frame, text="Work message:")
        self.work_message_label.grid(row=8, column=0, padx=20, pady=(10, 0), sticky="w")
        self.work_message_entry = ctk.CTkEntry(self.frame, textvariable=self.work_message_var, width=240)
        self.work_message_entry.grid(row=9, column=0, padx=20, pady=(5, 10), sticky="w")

        self.short_break_message_label = ctk.CTkLabel(self.frame, text="Short break message:")
        self.short_break_message_label.grid(row=10, column=0, padx=20, pady=(10, 0), sticky="w")
        self.short_break_message_entry = ctk.CTkEntry(self.frame, textvariable=self.short_break_message_var, width=240)
        self.short_break_message_entry.grid(row=11, column=0, padx=20, pady=(5, 10), sticky="w")

        self.long_break_message_label = ctk.CTkLabel(self.frame, text="Long break message:")
        self.long_break_message_label.grid(row=12, column=0, padx=20, pady=(10, 0), sticky="w")
        self.long_break_message_entry = ctk.CTkEntry(self.frame, textvariable=self.long_break_message_var, width=240)
        self.long_break_message_entry.grid(row=13, column=0, padx=20, pady=(5, 10), sticky="w")

        self.preview_var = tk.StringVar(value=self.timer.work_message)
        self.preview_label = ctk.CTkLabel(self.frame, text="Preview:", font=("Courier", 14, "bold"))
        self.preview_label.grid(row=14, column=0, padx=20, pady=(10, 0), sticky="w")
        self.preview_message_label = ctk.CTkLabel(self.frame, textvariable=self.preview_var, wraplength=260, justify="left")
        self.preview_message_label.grid(row=15, column=0, padx=20, pady=(5, 10), sticky="w")

        self.app_font_label = ctk.CTkLabel(self.frame, text="App font:")
        self.app_font_label.grid(row=16, column=0, padx=20, pady=(10, 0), sticky="w")
        self.app_font_menu = ctk.CTkOptionMenu(
            self.frame,
            values=config.APP_FONT_CHOICES,
            variable=self.app_font_var,
            command=lambda value: self._apply_changes()
        )
        self.app_font_menu.grid(row=17, column=0, padx=20, pady=(5, 10), sticky="w")

        self.message_font_label = ctk.CTkLabel(self.frame, text="Message font:")
        self.message_font_label.grid(row=18, column=0, padx=20, pady=(10, 0), sticky="w")
        self.message_font_menu = ctk.CTkOptionMenu(
            self.frame,
            values=config.MESSAGE_FONT_CHOICES,
            variable=self.message_font_var,
            command=lambda value: self._apply_changes()
        )
        self.message_font_menu.grid(row=19, column=0, padx=20, pady=(5, 10), sticky="w")

        self.long_break_message_label = ctk.CTkLabel(self.frame, text="Long break message:")
        self.long_break_message_label.grid(row=12, column=0, padx=20, pady=(10, 0), sticky="w")
        self.long_break_message_entry = ctk.CTkEntry(self.frame, textvariable=self.long_break_message_var, width=240)
        self.long_break_message_entry.grid(row=13, column=0, padx=20, pady=(5, 10), sticky="w")

        self.preview_var = tk.StringVar(value=self.timer.work_message)
        self.preview_label = ctk.CTkLabel(self.frame, text="Preview:", font=("Courier", 14, "bold"))
        self.preview_label.grid(row=14, column=0, padx=20, pady=(10, 0), sticky="w")
        self.preview_message_label = ctk.CTkLabel(self.frame, textvariable=self.preview_var, wraplength=260, justify="left")
        self.preview_message_label.grid(row=15, column=0, padx=20, pady=(5, 10), sticky="w")

        self.work_entry.bind("<FocusOut>", lambda e: self._apply_changes())
        self.work_entry.bind("<Return>", lambda e: self._apply_changes())
        self.short_break_entry.bind("<FocusOut>", lambda e: self._apply_changes())
        self.short_break_entry.bind("<Return>", lambda e: self._apply_changes())
        self.long_break_entry.bind("<FocusOut>", lambda e: self._apply_changes())
        self.long_break_entry.bind("<Return>", lambda e: self._apply_changes())
        self.work_message_entry.bind("<KeyRelease>", lambda e: self._update_preview())
        self.work_message_entry.bind("<FocusOut>", lambda e: self._apply_changes())
        self.work_message_entry.bind("<Return>", lambda e: self._apply_changes())
        self.short_break_message_entry.bind("<KeyRelease>", lambda e: self._update_preview())
        self.short_break_message_entry.bind("<FocusOut>", lambda e: self._apply_changes())
        self.short_break_message_entry.bind("<Return>", lambda e: self._apply_changes())
        self.long_break_message_entry.bind("<KeyRelease>", lambda e: self._update_preview())
        self.long_break_message_entry.bind("<FocusOut>", lambda e: self._apply_changes())
        self.long_break_message_entry.bind("<Return>", lambda e: self._apply_changes())

        self.theme_label = ctk.CTkLabel(self.frame, text="Theme:")
        self.theme_label.grid(row=16, column=0, padx=20, pady=(10, 0), sticky="w")
        self.theme_menu = ctk.CTkOptionMenu(self.frame, values=config.THEME_CHOICES, variable=self.theme_var, command=lambda value: self._apply_changes())
        self.theme_menu.grid(row=17, column=0, padx=20, pady=(5, 10), sticky="w")

        self.button_frame = ctk.CTkFrame(self.frame, fg_color=config.BG_COLOR, corner_radius=10)
        self.button_frame.grid(row=18, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        self.reset_button = ctk.CTkButton(
            self.button_frame,
            text="Reset to defaults",
            command=self.reset_to_defaults,
            fg_color="#e67e22",
            hover_color="#d35400"
        )
        self.reset_button.grid(row=0, column=0, padx=(0, 5), pady=10, sticky="ew")

        self.apply_messages_button = ctk.CTkButton(
            self.button_frame,
            text="Apply Messages",
            command=self.apply_message_changes,
            fg_color="#27ae60",
            hover_color="#2ecc71"
        )
        self.apply_messages_button.grid(row=0, column=1, padx=(5, 0), pady=10, sticky="ew")

        self.frame.grid(row=1, column=0, rowspan=5, sticky="nw", padx=20, pady=10)
        self.frame.grid_remove()

    def show(self):
        self.pause_option_var.set(self.timer.include_pause)
        self.skip_option_var.set(self.timer.include_skip)
        self.work_min_var.set(str(self.timer.work_min))
        self.short_break_min_var.set(str(self.timer.short_break_min))
        self.long_break_min_var.set(str(self.timer.long_break_min))
        self.work_message_var.set(self.timer.work_message)
        self.short_break_message_var.set(self.timer.short_break_message)
        self.long_break_message_var.set(self.timer.long_break_message)
        self.theme_var.set(self.timer.theme)
        self._update_preview()
        self.refresh_theme()
        self.frame.grid()
        self.frame.tkraise()
        self.visible = True

    def hide(self):
        self.frame.grid_remove()
        self.visible = False

    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    def refresh_theme(self):
        palette = self.timer.palette
        self.frame.configure(fg_color=palette["FRAME_BG"], border_color=palette["TEXT_COLOR"])
        self.pause_checkbox.configure(text_color=palette["TEXT_COLOR"], fg_color=palette["FRAME_BG"])
        self.work_label.configure(text_color=palette["TEXT_COLOR"])
        self.short_break_label.configure(text_color=palette["TEXT_COLOR"])
        self.long_break_label.configure(text_color=palette["TEXT_COLOR"])
        self.theme_label.configure(text_color=palette["TEXT_COLOR"])
        self.theme_menu.configure(button_color=palette["BUTTON_BG"], fg_color=palette["FRAME_BG"], text_color=palette["TEXT_COLOR"])
        self.button_frame.configure(fg_color=palette["APP_BG"])
        self.preview_label.configure(text_color=palette["TEXT_COLOR"], fg_color=palette["FRAME_BG"])
        self.preview_message_label.configure(text_color=palette["TEXT_COLOR"], fg_color=palette["FRAME_BG"])
        self.skip_checkbox.configure(text_color=palette["TEXT_COLOR"], fg_color=palette["FRAME_BG"])

    def _apply_changes(self):
        self.timer.pause_option_var.set(self.pause_option_var.get())
        self.timer.toggle_pause_option()
        self.timer.skip_option_var.set(self.skip_option_var.get())
        self.timer.toggle_skip_option()

        self.timer.work_min = self._parse_int(self.work_min_var.get(), self.timer.work_min)
        self.timer.short_break_min = self._parse_int(self.short_break_min_var.get(), self.timer.short_break_min)
        self.timer.long_break_min = self._parse_int(self.long_break_min_var.get(), self.timer.long_break_min)
        self.timer.work_message = self.work_message_var.get().strip() or self.timer.work_message
        self.timer.short_break_message = self.short_break_message_var.get().strip() or self.timer.short_break_message
        self.timer.long_break_message = self.long_break_message_var.get().strip() or self.timer.long_break_message
        self.timer.theme = self.theme_var.get()
        self._update_preview()
        self.timer.apply_theme()

        if not self.timer.is_running:
            self.timer.remaining_count = self.timer.work_min * 60
            self.timer.canvas.itemconfig(self.timer.time_text, text=f"{self.timer.work_min:02d}:00")

        self.timer.save_settings()

    def apply_message_changes(self):
        self.timer.work_message = self.work_message_var.get().strip() or self.timer.work_message
        self.timer.short_break_message = self.short_break_message_var.get().strip() or self.timer.short_break_message
        self.timer.long_break_message = self.long_break_message_var.get().strip() or self.timer.long_break_message
        self._update_preview()
        self.timer.save_settings()

    def _apply_skip_option_change(self):
        self.timer.skip_option_var.set(self.skip_option_var.get())
        self.timer.toggle_skip_option()

    def reset_to_defaults(self):
        self.pause_option_var.set(config.DEFAULT_SETTINGS["include_pause"])
        self.skip_option_var.set(config.DEFAULT_SETTINGS["include_skip"])
        self.work_min_var.set(str(config.DEFAULT_SETTINGS["work_min"]))
        self.short_break_min_var.set(str(config.DEFAULT_SETTINGS["short_break_min"]))
        self.long_break_min_var.set(str(config.DEFAULT_SETTINGS["long_break_min"]))
        self.work_message_var.set(config.DEFAULT_SETTINGS["work_message"])
        self.short_break_message_var.set(config.DEFAULT_SETTINGS["short_break_message"])
        self.long_break_message_var.set(config.DEFAULT_SETTINGS["long_break_message"])
        self.theme_var.set(config.DEFAULT_SETTINGS["theme"])
        self._apply_changes()

    def _parse_int(self, value, fallback):
        try:
            parsed = int(value)
            return parsed if parsed > 0 else fallback
        except ValueError:
            return fallback

    def _update_preview(self):
        current_title = self.timer.title_label.cget("text")
        if current_title == "Short Break":
            preview_text = self.short_break_message_var.get().strip() if self.short_break_message_var.get().strip() else self.timer.short_break_message
        elif current_title == "Long Break":
            preview_text = self.long_break_message_var.get().strip() if self.long_break_message_var.get().strip() else self.timer.long_break_message
        else:
            preview_text = self.work_message_var.get().strip() if self.work_message_var.get().strip() else self.timer.work_message
        self.preview_var.set(preview_text)
