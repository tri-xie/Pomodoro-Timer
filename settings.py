from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

import config


class SettingsPanel:
    def _apply_window_icon(self, window):
        try:
            path = getattr(self.timer, "app_icon_path", None)
            if path and os.path.isfile(path):
                if path.lower().endswith(".ico"):
                    window.iconbitmap(path)
                else:
                    image = ctk.CTkImage(light_image=Image.open(path), dark_image=Image.open(path), size=(32, 32))
                    window.iconphoto(True, image)
                    window._app_icon_image = image
        except Exception:
            pass


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
            height=520,
        )
        self.frame.grid_columnconfigure(0, weight=1)

        self.pause_option_var = tk.BooleanVar(value=timer.include_pause)
        self.skip_option_var = tk.BooleanVar(value=timer.include_skip)
        self.alert_option_var = tk.BooleanVar(value=timer.enable_session_alerts)
        self.notification_option_var = tk.BooleanVar(value=timer.show_notifications)
        self.volume_var = tk.DoubleVar(value=timer.alert_volume)
        self.notification_title_var = tk.StringVar(value=timer.notification_title)
        self.notification_message_var = tk.StringVar(value=timer.notification_message)
        self.work_min_var = tk.StringVar(value=str(timer.work_min))
        self.short_break_min_var = tk.StringVar(value=str(timer.short_break_min))
        self.long_break_min_var = tk.StringVar(value=str(timer.long_break_min))
        self.work_message_var = tk.StringVar(value=timer.work_message)
        self.short_break_message_var = tk.StringVar(value=timer.short_break_message)
        self.long_break_message_var = tk.StringVar(value=timer.long_break_message)
        self.app_font_var = tk.StringVar(value=timer.app_font_family)
        self.message_font_var = tk.StringVar(value=timer.message_font_family)
        self.theme_var = tk.StringVar(value=timer.theme)
        self.sound_vars = {s: tk.StringVar(value=timer.sound_settings[s]) for s in ("Work", "Short Break", "Long Break")}
        self.custom_sound_vars = {s: tk.StringVar(value=timer.custom_sound_paths[s]) for s in ("Work", "Short Break", "Long Break")}
        self.sound_widgets = {}

        row = 0
        self.pause_checkbox = ctk.CTkCheckBox(self.frame, text="Enable Pause", variable=self.pause_option_var, command=self._apply_changes)
        self.pause_checkbox.grid(row=row, column=0, padx=20, pady=(20, 10), sticky="w"); row += 1
        self.skip_checkbox = ctk.CTkCheckBox(self.frame, text="Enable Skip", variable=self.skip_option_var, command=self._apply_skip_option_change)
        self.skip_checkbox.grid(row=row, column=0, padx=20, pady=(0, 10), sticky="w"); row += 1
        self.alert_checkbox = ctk.CTkCheckBox(self.frame, text="Enable session alerts", variable=self.alert_option_var, command=self._apply_alert_option_change)
        self.alert_checkbox.grid(row=row, column=0, padx=20, pady=(0, 10), sticky="w"); row += 1
        self.notification_checkbox = ctk.CTkCheckBox(self.frame, text="Show desktop notifications", variable=self.notification_option_var, command=self._apply_notification_changes)
        self.notification_checkbox.grid(row=row, column=0, padx=20, pady=(0, 10), sticky="w"); row += 1

        self.volume_label = ctk.CTkLabel(self.frame, text="Alert volume:")
        self.volume_label.grid(row=row, column=0, padx=20, pady=(5, 0), sticky="w"); row += 1
        self.volume_slider = ctk.CTkSlider(self.frame, from_=0, to=100, variable=self.volume_var, command=self._apply_volume_change, width=240)
        self.volume_slider.grid(row=row, column=0, padx=20, pady=(5, 2), sticky="w"); row += 1
        self.volume_value_label = ctk.CTkLabel(self.frame, text=f"{int(timer.alert_volume)}%")
        self.volume_value_label.grid(row=row, column=0, padx=20, pady=(0, 10), sticky="w"); row += 1

        self.notification_title_label = ctk.CTkLabel(self.frame, text="Notification title:")
        self.notification_title_label.grid(row=row, column=0, padx=20, pady=(5, 0), sticky="w"); row += 1
        self.notification_title_entry = ctk.CTkEntry(self.frame, textvariable=self.notification_title_var, width=260)
        self.notification_title_entry.grid(row=row, column=0, padx=20, pady=(5, 10), sticky="w"); row += 1
        self.notification_message_label = ctk.CTkLabel(self.frame, text="Notification message ({session} = session name):")
        self.notification_message_label.grid(row=row, column=0, padx=20, pady=(5, 0), sticky="w"); row += 1
        self.notification_message_entry = ctk.CTkEntry(self.frame, textvariable=self.notification_message_var, width=260)
        self.notification_message_entry.grid(row=row, column=0, padx=20, pady=(5, 10), sticky="w"); row += 1

        self.sound_title = ctk.CTkLabel(self.frame, text="Session sounds:", font=(timer.app_font_family, 14, "bold"))
        self.sound_title.grid(row=row, column=0, padx=20, pady=(10, 5), sticky="w"); row += 1
        for session in ("Work", "Short Break", "Long Break"):
            label = ctk.CTkLabel(self.frame, text=f"{session} complete:")
            label.grid(row=row, column=0, padx=20, pady=(5, 0), sticky="w"); row += 1
            menu = ctk.CTkOptionMenu(self.frame, values=config.SOUND_CHOICES, variable=self.sound_vars[session], command=lambda _v, s=session: self._apply_sound_change(s))
            menu.grid(row=row, column=0, padx=20, pady=(5, 5), sticky="w"); row += 1
            browse = ctk.CTkButton(self.frame, text="Browse custom...", width=140, command=lambda s=session: self._browse_custom_sound(s))
            browse.grid(row=row, column=0, padx=20, pady=(2, 2), sticky="w"); row += 1
            test = ctk.CTkButton(self.frame, text="Test sound/notification", width=180, command=lambda s=session: self.timer.test_session_alert(s))
            test.grid(row=row, column=0, padx=20, pady=(2, 2), sticky="w"); row += 1
            path_label = ctk.CTkLabel(self.frame, textvariable=self.custom_sound_vars[session], wraplength=280, justify="left")
            path_label.grid(row=row, column=0, padx=20, pady=(0, 8), sticky="w"); row += 1
            self.sound_widgets[session] = (label, menu, browse, test, path_label)

        self.work_label = ctk.CTkLabel(self.frame, text="Work duration (minutes):")
        self.work_label.grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w"); row += 1
        self.work_entry = ctk.CTkEntry(self.frame, textvariable=self.work_min_var, width=120)
        self.work_entry.grid(row=row, column=0, padx=20, pady=(5, 10), sticky="w"); row += 1
        self.short_break_label = ctk.CTkLabel(self.frame, text="Short break (minutes):")
        self.short_break_label.grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w"); row += 1
        self.short_break_entry = ctk.CTkEntry(self.frame, textvariable=self.short_break_min_var, width=120)
        self.short_break_entry.grid(row=row, column=0, padx=20, pady=(5, 10), sticky="w"); row += 1
        self.long_break_label = ctk.CTkLabel(self.frame, text="Long break (minutes):")
        self.long_break_label.grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w"); row += 1
        self.long_break_entry = ctk.CTkEntry(self.frame, textvariable=self.long_break_min_var, width=120)
        self.long_break_entry.grid(row=row, column=0, padx=20, pady=(5, 10), sticky="w"); row += 1

        self.work_message_label = ctk.CTkLabel(self.frame, text="Work message:")
        self.work_message_label.grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w"); row += 1
        self.work_message_entry = ctk.CTkEntry(self.frame, textvariable=self.work_message_var, width=260)
        self.work_message_entry.grid(row=row, column=0, padx=20, pady=(5, 10), sticky="w"); row += 1
        self.short_break_message_label = ctk.CTkLabel(self.frame, text="Short break message:")
        self.short_break_message_label.grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w"); row += 1
        self.short_break_message_entry = ctk.CTkEntry(self.frame, textvariable=self.short_break_message_var, width=260)
        self.short_break_message_entry.grid(row=row, column=0, padx=20, pady=(5, 10), sticky="w"); row += 1
        self.long_break_message_label = ctk.CTkLabel(self.frame, text="Long break message:")
        self.long_break_message_label.grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w"); row += 1
        self.long_break_message_entry = ctk.CTkEntry(self.frame, textvariable=self.long_break_message_var, width=260)
        self.long_break_message_entry.grid(row=row, column=0, padx=20, pady=(5, 10), sticky="w"); row += 1

        self.preview_var = tk.StringVar(value=timer.work_message)
        self.preview_label = ctk.CTkLabel(self.frame, text="Preview:", font=(timer.app_font_family, 14, "bold"))
        self.preview_label.grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w"); row += 1
        self.preview_message_label = ctk.CTkLabel(self.frame, textvariable=self.preview_var, wraplength=280, justify="left")
        self.preview_message_label.grid(row=row, column=0, padx=20, pady=(5, 10), sticky="w"); row += 1

        self.app_font_label = ctk.CTkLabel(self.frame, text="App font:")
        self.app_font_label.grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w"); row += 1
        self.app_font_menu = ctk.CTkOptionMenu(self.frame, values=config.APP_FONT_CHOICES, variable=self.app_font_var, command=lambda _v: self._apply_changes())
        self.app_font_menu.grid(row=row, column=0, padx=20, pady=(5, 10), sticky="w"); row += 1
        self.message_font_label = ctk.CTkLabel(self.frame, text="Message font:")
        self.message_font_label.grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w"); row += 1
        self.message_font_menu = ctk.CTkOptionMenu(self.frame, values=config.MESSAGE_FONT_CHOICES, variable=self.message_font_var, command=lambda _v: self._apply_changes())
        self.message_font_menu.grid(row=row, column=0, padx=20, pady=(5, 10), sticky="w"); row += 1
        self.theme_label = ctk.CTkLabel(self.frame, text="Theme:")
        self.theme_label.grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w"); row += 1
        self.theme_menu = ctk.CTkOptionMenu(self.frame, values=config.THEME_CHOICES, variable=self.theme_var, command=lambda _v: self._apply_changes())
        self.theme_menu.grid(row=row, column=0, padx=20, pady=(5, 10), sticky="w"); row += 1

        self.custom_theme_button = ctk.CTkButton(
            self.frame,
            text="Custom Theme",
            command=self.timer.toggle_theme_customizer,
        )
        self.custom_theme_button.grid(
            row=row, column=0, padx=20, pady=(10, 8), sticky="ew"
        )
        row += 1

        self.button_frame = ctk.CTkFrame(self.frame, fg_color=config.BG_COLOR, corner_radius=10)
        self.button_frame.grid(row=row, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)
        self.reset_button = ctk.CTkButton(self.button_frame, text="Reset to defaults", command=self.reset_to_defaults, fg_color="#e67e22", hover_color="#d35400")
        self.reset_button.grid(row=0, column=0, padx=(0, 5), pady=10, sticky="ew")
        self.apply_messages_button = ctk.CTkButton(self.button_frame, text="Apply Messages", command=self.apply_message_changes, fg_color="#27ae60", hover_color="#2ecc71")
        self.apply_messages_button.grid(row=0, column=1, padx=(5, 0), pady=10, sticky="ew")

        self.frame.grid(row=1, column=0, rowspan=5, sticky="nw", padx=20, pady=10)
        self.frame.grid_remove()

        for entry in (self.work_entry, self.short_break_entry, self.long_break_entry):
            entry.bind("<FocusOut>", lambda _e: self._apply_changes())
            entry.bind("<Return>", lambda _e: self._apply_changes())
        for entry in (self.work_message_entry, self.short_break_message_entry, self.long_break_message_entry):
            entry.bind("<KeyRelease>", lambda _e: self._update_preview())
            entry.bind("<FocusOut>", lambda _e: self._apply_changes())
            entry.bind("<Return>", lambda _e: self._apply_changes())
        self.notification_title_entry.bind("<FocusOut>", lambda _e: self._apply_changes())
        self.notification_message_entry.bind("<FocusOut>", lambda _e: self._apply_changes())

    def show(self):
        self.pause_option_var.set(self.timer.include_pause)
        self.skip_option_var.set(self.timer.include_skip)
        self.alert_option_var.set(self.timer.enable_session_alerts)
        self.notification_option_var.set(self.timer.show_notifications)
        self.volume_var.set(self.timer.alert_volume)
        self.volume_value_label.configure(text=f"{int(self.timer.alert_volume)}%")
        self.notification_title_var.set(self.timer.notification_title)
        self.notification_message_var.set(self.timer.notification_message)
        self.work_min_var.set(str(self.timer.work_min))
        self.short_break_min_var.set(str(self.timer.short_break_min))
        self.long_break_min_var.set(str(self.timer.long_break_min))
        self.work_message_var.set(self.timer.work_message)
        self.short_break_message_var.set(self.timer.short_break_message)
        self.long_break_message_var.set(self.timer.long_break_message)
        self.app_font_var.set(self.timer.app_font_family)
        self.message_font_var.set(self.timer.message_font_family)
        self.theme_var.set(self.timer.theme)
        for session in self.sound_vars:
            self.sound_vars[session].set(self.timer.sound_settings[session])
            self.custom_sound_vars[session].set(self.timer.custom_sound_paths[session])
        self._update_preview()
        self.refresh_theme()
        self.frame.grid(); self.frame.tkraise(); self.visible = True

    def hide(self):
        self.frame.grid_remove(); self.visible = False

    def toggle(self):
        self.hide() if self.visible else self.show()

    def refresh_theme(self):
        palette = self.timer.palette
        self.frame.configure(fg_color=palette["FRAME_BG"], border_color=palette["TEXT_COLOR"])
        checks = (self.pause_checkbox, self.skip_checkbox, self.alert_checkbox, self.notification_checkbox)
        labels = (self.volume_label, self.notification_title_label, self.notification_message_label, self.sound_title,
                  self.work_label, self.short_break_label, self.long_break_label, self.work_message_label,
                  self.short_break_message_label, self.long_break_message_label, self.app_font_label,
                  self.message_font_label, self.theme_label, self.preview_label)
        for w in checks + labels:
            w.configure(text_color=palette["TEXT_COLOR"], bg_color=palette["FRAME_BG"])
        for w in (self.work_entry, self.short_break_entry, self.long_break_entry, self.work_message_entry,
                  self.short_break_message_entry, self.long_break_message_entry, self.notification_title_entry,
                  self.notification_message_entry):
            w.configure(text_color=palette["TEXT_COLOR"], fg_color=palette["APP_BG"], border_color=palette["TEXT_COLOR"])
        for w in (self.app_font_menu, self.message_font_menu, self.theme_menu) + tuple(x[1] for x in self.sound_widgets.values()):
            w.configure(button_color=palette["BUTTON_BG"], fg_color=palette["FRAME_BG"], text_color=palette["TEXT_COLOR"])
        self.volume_slider.configure(progress_color=palette["BUTTON_BG"], button_color=palette["TEXT_COLOR"])
        self.preview_message_label.configure(text_color=palette["TEXT_COLOR"], bg_color=palette["FRAME_BG"])
        for widgets in self.sound_widgets.values():
            for w in (widgets[0], widgets[3], widgets[4]):
                w.configure(text_color=palette["TEXT_COLOR"], bg_color=palette["FRAME_BG"])
        self.button_frame.configure(fg_color=palette["APP_BG"])
        self.custom_theme_button.configure(fg_color=palette["BUTTON_BG"], hover_color=palette["BUTTON_BG"], text_color=palette["TEXT_COLOR"])

    def _apply_changes(self):
        self.timer.pause_option_var.set(self.pause_option_var.get()); self.timer.toggle_pause_option()
        self.timer.skip_option_var.set(self.skip_option_var.get()); self.timer.toggle_skip_option()
        self.timer.enable_session_alerts = self.alert_option_var.get()
        self.timer.show_notifications = self.notification_option_var.get()
        self.timer.alert_volume = max(0, min(100, int(float(self.volume_var.get()))))
        self.volume_value_label.configure(text=f"{self.timer.alert_volume}%")
        self.timer.notification_title = self.notification_title_var.get().strip() or config.NOTIFICATION_TITLE
        self.timer.notification_message = self.notification_message_var.get().strip() or config.NOTIFICATION_MESSAGE
        self.timer.work_min = self._parse_int(self.work_min_var.get(), self.timer.work_min)
        self.timer.short_break_min = self._parse_int(self.short_break_min_var.get(), self.timer.short_break_min)
        self.timer.long_break_min = self._parse_int(self.long_break_min_var.get(), self.timer.long_break_min)
        self.timer.work_message = self.work_message_var.get().strip() or self.timer.work_message
        self.timer.short_break_message = self.short_break_message_var.get().strip() or self.timer.short_break_message
        self.timer.long_break_message = self.long_break_message_var.get().strip() or self.timer.long_break_message
        if self.app_font_var.get() in config.APP_FONT_CHOICES: self.timer.app_font_family = self.app_font_var.get()
        if self.message_font_var.get() in config.MESSAGE_FONT_CHOICES: self.timer.message_font_family = self.message_font_var.get()
        if self.theme_var.get() in config.THEME_CHOICES: self.timer.theme = self.theme_var.get()
        for session in self.sound_vars:
            self.timer.sound_settings[session] = self.sound_vars[session].get()
            self.timer.custom_sound_paths[session] = self.custom_sound_vars[session].get().strip()
        self._update_preview(); self.timer.apply_fonts(); self.timer.apply_theme()
        if not self.timer.is_running:
            self.timer.remaining_count = self.timer.work_min * 60
            self.timer.canvas.itemconfig(self.timer.time_text, text=f"{self.timer.work_min:02d}:00")
            self.timer.title_label.configure(text="Timer")
            self.timer.message_label.configure(text=self.timer.work_message)
        self.timer.save_settings()

    def apply_message_changes(self):
        self.timer.work_message = self.work_message_var.get().strip() or self.timer.work_message
        self.timer.short_break_message = self.short_break_message_var.get().strip() or self.timer.short_break_message
        self.timer.long_break_message = self.long_break_message_var.get().strip() or self.timer.long_break_message
        self._update_preview(); self.timer.save_settings()

    def _apply_alert_option_change(self): self.timer.enable_session_alerts = self.alert_option_var.get(); self.timer.save_settings()
    def _apply_notification_changes(self): self.timer.show_notifications = self.notification_option_var.get(); self.timer.save_settings()
    def _apply_volume_change(self, value):
        self.timer.alert_volume = max(0, min(100, int(float(value))))
        self.volume_value_label.configure(text=f"{self.timer.alert_volume}%")
        self.timer.save_settings()
    def _apply_sound_change(self, session): self.timer.sound_settings[session] = self.sound_vars[session].get(); self.timer.save_settings()
    def _apply_skip_option_change(self): self.timer.skip_option_var.set(self.skip_option_var.get()); self.timer.toggle_skip_option(); self.timer.save_settings()

    def _browse_custom_sound(self, session):
        path = filedialog.askopenfilename(title=f"Choose {session} alert sound", filetypes=[("WAV audio", "*.wav"), ("All files", "*.*")])
        if path:
            self.custom_sound_vars[session].set(path)
            self.timer.custom_sound_paths[session] = path
            self.sound_vars[session].set("Custom")
            self.timer.sound_settings[session] = "Custom"
            self.timer.save_settings()

    def reset_to_defaults(self):
        d = config.DEFAULT_SETTINGS
        self.pause_option_var.set(d["include_pause"]); self.skip_option_var.set(d["include_skip"])
        self.alert_option_var.set(d["enable_session_alerts"]); self.notification_option_var.set(d["show_notifications"])
        self.volume_var.set(d["alert_volume"]); self.notification_title_var.set(d["notification_title"]); self.notification_message_var.set(d["notification_message"])
        self.work_min_var.set(str(d["work_min"])); self.short_break_min_var.set(str(d["short_break_min"])); self.long_break_min_var.set(str(d["long_break_min"]))
        self.work_message_var.set(d["work_message"]); self.short_break_message_var.set(d["short_break_message"]); self.long_break_message_var.set(d["long_break_message"])
        self.app_font_var.set(d["app_font_family"]); self.message_font_var.set(d["message_font_family"]); self.theme_var.set(d["theme"])
        for session, key in (("Work", "work_sound"), ("Short Break", "short_break_sound"), ("Long Break", "long_break_sound")):
            self.sound_vars[session].set(d[key]); self.custom_sound_vars[session].set("")
        self._apply_changes()

    @staticmethod
    def _parse_int(value, fallback):
        try:
            parsed = int(value); return parsed if parsed > 0 else fallback
        except (TypeError, ValueError): return fallback

    def _update_preview(self):
        current_title = self.timer.title_label.cget("text")
        if current_title == "Short Break": text = self.short_break_message_var.get().strip() or self.timer.short_break_message
        elif current_title == "Long Break": text = self.long_break_message_var.get().strip() or self.timer.long_break_message
        else: text = self.work_message_var.get().strip() or self.timer.work_message
        self.preview_var.set(text)
