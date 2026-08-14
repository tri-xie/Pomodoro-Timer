from PIL import Image, ImageTk
import tkinter as tk
import tkinter.font as tkfont
import os
import subprocess
import sys
import customtkinter as ctk

import config
from settings import SettingsPanel
from history import SessionHistory
from tasks import TaskStore
from scheduler import SchedulerPanel
from themes import ThemeStore
from theme_customizer import ThemeCustomizer
from stats import StatsPanel


class PomodoroTimer:
    def __init__(self, root, include_pause=config.INCLUDE_PAUSE_BUTTON):
        self.root = root
        self.app_icon_path = os.path.join(os.path.dirname(__file__), "app logo.ico")
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
        self.work_message = user_settings.get("work_message", config.DEFAULT_SETTINGS["work_message"])
        self.short_break_message = user_settings.get("short_break_message", config.DEFAULT_SETTINGS["short_break_message"])
        self.long_break_message = user_settings.get("long_break_message", config.DEFAULT_SETTINGS["long_break_message"])
        self.app_font_family = user_settings.get("app_font_family", config.DEFAULT_SETTINGS["app_font_family"])
        self.message_font_family = user_settings.get("message_font_family", config.DEFAULT_SETTINGS["message_font_family"])
        self.include_skip = user_settings.get("include_skip", config.INCLUDE_SKIP_BUTTON)
        self.enable_session_alerts = user_settings.get("enable_session_alerts", config.ENABLE_SESSION_ALERTS)
        self.alert_volume = user_settings.get("alert_volume", config.ALERT_VOLUME)
        self.show_notifications = user_settings.get("show_notifications", config.SHOW_NOTIFICATIONS)
        self.notification_title = user_settings.get("notification_title", config.NOTIFICATION_TITLE)
        self.notification_message = user_settings.get("notification_message", config.NOTIFICATION_MESSAGE)
        self.sound_settings = {
            "Work": user_settings.get("work_sound", config.WORK_SOUND),
            "Short Break": user_settings.get("short_break_sound", config.SHORT_BREAK_SOUND),
            "Long Break": user_settings.get("long_break_sound", config.LONG_BREAK_SOUND),
        }
        self.custom_sound_paths = {
            "Work": user_settings.get("work_custom_sound", config.WORK_CUSTOM_SOUND),
            "Short Break": user_settings.get("short_break_custom_sound", config.SHORT_BREAK_CUSTOM_SOUND),
            "Long Break": user_settings.get("long_break_custom_sound", config.LONG_BREAK_CUSTOM_SOUND),
        }
        self.pause_button = None
        self.skip_button = None
        self.pause_option_var = tk.BooleanVar(value=self.include_pause)
        self.skip_option_var = tk.BooleanVar(value=self.include_skip)
        self.settings_panel = None
        
        # Core data stores
        self.history = SessionHistory(config.HISTORY_PATH)
        self.task_store = TaskStore(config.TASKS_PATH)
        self.theme_store = ThemeStore(config.THEME_PATH)
        self._background_image_ref = None
        self.current_task_id = None

        self.title_label = ctk.CTkLabel(
            self.root,
            text="Timer",
            text_color=self.palette["TEXT_COLOR"],
            bg_color=self.palette["APP_BG"],
            font=(self.app_font_family, 35, "bold")
        )
        self.title_label.grid(column=1, row=1, pady=(10, 0))

        self.canvas = tk.Canvas(
            self.root,
            width=200,
            height=224,
            bg=self.palette["CANVAS_BG"],
            highlightthickness=0
        )
        self.time_font = tkfont.Font(family=self.app_font_family, size=35, weight="bold")
        self.time_text = self.canvas.create_text(
            100, 112, text=f"{self.work_min:02d}:00", fill=self.palette["TEXT_COLOR"], font=self.time_font
        )
        self.canvas.grid(column=1, row=2, pady=20)

        self.button_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.palette["APP_BG"],
            corner_radius=0
        )
        self.button_frame.grid(column=1, row=4, pady=(0, 10), sticky="ew")
        self._configure_button_frame_columns()

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
        self.reset_button.grid(column=1, row=0, padx=(5, 10), pady=5, sticky="ew")

        if self.include_pause:
            self.create_pause_button()
        if self.include_skip:
            self.create_skip_button()
        self._update_button_layout()

        self.message_label = ctk.CTkLabel(
            self.root,
            text=self.work_message,
            text_color=self.palette["TEXT_COLOR"],
            bg_color=self.palette["APP_BG"],
            font=(self.message_font_family, 16)
        )
        self.message_label.grid(column=1, row=3, pady=(0, 8))

        self.top_actions_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.top_actions_frame.grid(column=1, row=0, pady=(10, 0))
        self.top_actions_frame.grid_columnconfigure(0, weight=1)
        self.top_actions_frame.grid_columnconfigure(1, weight=1)

        self.stats_button = ctk.CTkButton(
            self.top_actions_frame,
            text="Session Stats",
            command=self.toggle_stats_panel,
            fg_color=self.palette["BUTTON_BG"],
            hover_color=self.palette["BUTTON_BG"],
            text_color=self.palette["TEXT_COLOR"],
            width=130,
            height=34,
            corner_radius=17,
        )
        self.stats_button.grid(column=0, row=0, padx=(0, 4), sticky="ew")

        self.schedule_button = ctk.CTkButton(
            self.top_actions_frame, text="Schedule Focus",
            command=self.toggle_scheduler_panel,
            fg_color=self.palette["BUTTON_BG"],
            hover_color=self.palette["BUTTON_BG"],
            text_color=self.palette["TEXT_COLOR"],
            width=130, height=34, corner_radius=17,
        )
        self.schedule_button.grid(column=1, row=0, padx=(4, 0), sticky="ew")

        self.menu_button = ctk.CTkButton(
            self.root,
            text="⚙",
            command=self.toggle_settings_panel,
            fg_color=self.palette["BUTTON_BG"],
            hover_color=self.palette["BUTTON_BG"],
            text_color=self.palette["TEXT_COLOR"],
            width=60,
            height=40,
            corner_radius=20,
        )
        self.menu_button.grid(column=0, row=0, padx=(10, 0), pady=(10, 0), sticky="w")

        self.settings_panel = SettingsPanel(self.root, self)
        self.stats_panel = StatsPanel(self.root, self)
        self.scheduler_panel = SchedulerPanel(self.root, self)
        self.theme_customizer = ThemeCustomizer(self.root, self)
        self.apply_custom_theme()

        self.check_marks = ctk.CTkLabel(
            self.root,
            text="",
            text_color="#9bdeac",
            bg_color=self.palette["APP_BG"],
            font=(self.app_font_family, 18)
        )
        self.check_marks.grid(column=1, row=5, pady=(16, 0))
        self.apply_fonts()
        self.apply_theme()

    def reset_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
            
        self.reps = 0
        self.is_running = False
        self.is_paused = False
        self.current_task_id = None # Clear bound task id if reset
        
        self.remaining_count = self.work_min * 60
        self.canvas.itemconfig(self.time_text, text=f"{self.work_min:02d}:00")
        self.title_label.configure(text="Timer", text_color=self.palette["TEXT_COLOR"])
        self.check_marks.configure(text="")
        self.message_label.configure(text=self.work_message)
        self.start_button.configure(state="normal")
        
        if self.include_pause and self.pause_button:
            self.pause_button.configure(state="disabled", text="Pause")
        if self.include_skip and self.skip_button:
            self.skip_button.configure(state="disabled")

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
        self._update_button_layout()

    def create_skip_button(self):
        if self.skip_button:
            return
        self.skip_button = ctk.CTkButton(
            self.button_frame,
            text="Skip",
            command=self.skip_session,
            fg_color="#3498db",
            hover_color="#2980b9",
            state="disabled"
        )
        self._update_button_layout()

    def _configure_button_frame_columns(self):
        active_count = 2 + int(self.pause_button is not None) + int(self.skip_button is not None)
        for i in range(4):
            self.button_frame.grid_columnconfigure(i, weight=0, minsize=0, uniform="")
        for i in range(active_count):
            self.button_frame.grid_columnconfigure(i, weight=1, minsize=0, uniform="active_timer_controls")

    def _update_button_layout(self):
        self._configure_button_frame_columns()
        self.start_button.grid_forget()
        if self.pause_button:
            self.pause_button.grid_forget()
        if self.skip_button:
            self.skip_button.grid_forget()
        self.reset_button.grid_forget()

        active = [self.start_button]
        if self.pause_button:
            active.append(self.pause_button)
        if self.skip_button:
            active.append(self.skip_button)
        active.append(self.reset_button)

        for column, button in enumerate(active):
            button.grid(column=column, row=0, padx=4, pady=5, sticky="ew")

    def destroy_pause_button(self):
        if self.pause_button:
            self.pause_button.destroy()
            self.pause_button = None
        self._update_button_layout()

    def destroy_skip_button(self):
        if self.skip_button:
            self.skip_button.destroy()
            self.skip_button = None
        self._update_button_layout()

    def toggle_pause_option(self):
        self.include_pause = self.pause_option_var.get()
        if self.include_pause:
            self.create_pause_button()
            if self.pause_button:
                self.pause_button.configure(state="normal" if self.is_running else "disabled")
        else:
            self.destroy_pause_button()
        self._update_button_layout()

    def toggle_skip_option(self):
        self.include_skip = self.skip_option_var.get()
        if self.include_skip:
            self.create_skip_button()
            if self.skip_button:
                self.skip_button.configure(state="normal" if self.is_running else "disabled")
        else:
            self.destroy_skip_button()
        self._update_button_layout()

    def toggle_settings_panel(self):
        self.settings_panel.toggle()

    def apply_fonts(self):
        self.time_font.configure(family=self.app_font_family)
        self.title_label.configure(font=(self.app_font_family, 35, "bold"))
        self.message_label.configure(font=(self.message_font_family, 16))
        self.menu_button.configure(font=(self.app_font_family, 16, "bold"))
        self.start_button.configure(font=(self.app_font_family, 14, "bold"))
        self.reset_button.configure(font=(self.app_font_family, 14, "bold"))
        if self.pause_button:
            self.pause_button.configure(font=(self.app_font_family, 14, "bold"))
        if self.skip_button:
            self.skip_button.configure(font=(self.app_font_family, 14, "bold"))
        self.check_marks.configure(font=(self.app_font_family, 18))

    def _prepare_child_window(self, attr_name, title=None):
        """Prevent duplicate/layered auxiliary windows."""
        existing = getattr(self, attr_name, None)
        try:
            if existing is not None and existing.winfo_exists():
                existing.lift()
                existing.focus_force()
                return existing
        except Exception:
            pass
        return None

    def clear_custom_theme(self):
        """Remove custom-theme visual overrides and restore the active preset palette."""
        try:
            if hasattr(self, "background_label") and self.background_label.winfo_exists():
                self.background_label.destroy()
                del self.background_label
        except Exception:
            pass
        try:
            self.root.configure(fg_color=self.palette["APP_BG"], bg=self.palette["APP_BG"])
        except Exception:
            pass

    def set_standard_appearance_mode(self, mode):
        """Switch Light/Dark/System and explicitly replace custom-theme visuals."""
        if mode not in ("Light", "Dark", "System"):
            mode = "System"
        self.clear_custom_theme()
        ctk.set_appearance_mode(mode)
        self.apply_theme()

    def apply_theme(self):
        if self.theme not in config.THEME_PALETTES:
            self.theme = config.DEFAULT_THEME
        self.palette = config.THEME_PALETTES[self.theme]
        appearance_mode = self.theme if self.theme in ("Light", "Dark", "System") else "System"
        ctk.set_appearance_mode(appearance_mode)
        self.root.configure(bg=self.palette["APP_BG"])
        self.title_label.configure(bg_color=self.palette["APP_BG"], text_color=self.palette["TEXT_COLOR"])
        self.canvas.configure(bg=self.palette["CANVAS_BG"])
        self.canvas.itemconfig(self.time_text, fill=self.palette["TEXT_COLOR"])
        self.button_frame.configure(fg_color=self.palette["APP_BG"])
        self.check_marks.configure(bg_color=self.palette["APP_BG"], text_color=self.palette["TEXT_COLOR"])
        self.settings_panel.refresh_theme()

    def start_scheduled_task(self, task):
        self.current_task_id = task.get("id")
        title = task.get("title", "Focus Session")
        if hasattr(self, "message_label"):
            self.message_label.configure(text=title)
        minutes = int(task.get("duration_minutes", self.work_min))
        self.work_min = minutes
        self.reset_timer()
        
        # Ensure task ID persists through the reset that just happened
        self.current_task_id = task.get("id")
        self.start_timer()

    def apply_custom_theme(self):
        colors = self.theme_store.colors
        self.root.configure(fg_color=colors["bg_start"])
        for name in ("title_label", "timer_label", "message_label", "check_marks"):
            if hasattr(self, name):
                getattr(self, name).configure(text_color=colors["text"])
        for name in ("start_button", "pause_button", "skip_button", "reset_button",
                     "stats_button", "schedule_button", "theme_button"):
            if hasattr(self, name):
                try:
                    getattr(self, name).configure(
                        fg_color=colors["accent"],
                        hover_color=colors["accent"],
                        text_color=colors["text"]
                    )
                except Exception:
                    pass
        path = self.theme_store.data.get("background_image", "")
        if path and os.path.isfile(path):
            try:
                image = Image.open(path)
                image = image.resize((max(self.root.winfo_width(), 700), max(self.root.winfo_height(), 600)))
                self._background_image_ref = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
            except Exception:
                self._background_image_ref = None

    def toggle_theme_customizer(self):
        existing = self._prepare_child_window("theme_window")
        if existing is not None:
            return
        if self.theme_customizer.visible:
            self.theme_customizer.hide()
        else:
            self.theme_customizer.show()

    def toggle_scheduler_panel(self):
        if self.scheduler_panel.visible:
            self.scheduler_panel.hide()
        else:
            self.scheduler_panel.show()

    def toggle_stats_panel(self):
        if self.stats_panel.visible:
            self.stats_panel.hide()
        else:
            self.stats_panel.show()

    def save_settings(self):
        config.save_user_settings({
            "theme": self.theme,
            "work_min": self.work_min,
            "short_break_min": self.short_break_min,
            "long_break_min": self.long_break_min,
            "work_message": self.work_message,
            "short_break_message": self.short_break_message,
            "long_break_message": self.long_break_message,
            "app_font_family": self.app_font_family,
            "message_font_family": self.message_font_family,
            "include_pause": self.include_pause,
            "include_skip": self.include_skip,
            "enable_session_alerts": self.enable_session_alerts,
            "alert_volume": self.alert_volume,
            "show_notifications": self.show_notifications,
            "notification_title": self.notification_title,
            "notification_message": self.notification_message,
            "work_sound": self.sound_settings["Work"],
            "short_break_sound": self.sound_settings["Short Break"],
            "long_break_sound": self.sound_settings["Long Break"],
            "work_custom_sound": self.custom_sound_paths["Work"],
            "short_break_custom_sound": self.custom_sound_paths["Short Break"],
            "long_break_custom_sound": self.custom_sound_paths["Long Break"],
        })

    def _play_custom_wav(self, path, volume):
        if not path or not os.path.isfile(path):
            return False
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            sound = pygame.mixer.Sound(path)
            sound.set_volume(max(0, min(100, volume)) / 100.0)
            sound.play()
            return True
        except Exception:
            return False

    def _play_session_sound(self, session_name):
        choice = self.sound_settings.get(session_name, "System Default")
        if choice == "None":
            return
        if choice == "Custom" and self._play_custom_wav(self.custom_sound_paths.get(session_name, ""), self.alert_volume):
            return
        try:
            if sys.platform.startswith("win"):
                import winsound
                sounds = {
                    "System Default": winsound.MB_OK,
                    "Information": winsound.MB_ICONASTERISK,
                    "Warning": winsound.MB_ICONEXCLAMATION,
                    "Error": winsound.MB_ICONHAND,
                }
                winsound.MessageBeep(sounds.get(choice, winsound.MB_OK))
            elif sys.platform == "darwin":
                sound_file = {
                    "System Default": "/System/Library/Sounds/Glass.aiff",
                    "Information": "/System/Library/Sounds/Ping.aiff",
                    "Warning": "/System/Library/Sounds/Basso.aiff",
                    "Error": "/System/Library/Sounds/Sosumi.aiff",
                }.get(choice, "/System/Library/Sounds/Glass.aiff")
                subprocess.Popen(["afplay", "-v", str(self.alert_volume / 100), sound_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                self.root.bell()
        except Exception:
            try:
                self.root.bell()
            except Exception:
                pass

    def play_session_alert(self, session_name):
        if not self.enable_session_alerts:
            return
        self._play_session_sound(session_name)
        if not self.show_notifications:
            return
        try:
            from plyer import notification
            message = self.notification_message.replace("{session}", session_name)
            notification.notify(title=self.notification_title, message=message, app_name="Pomodoro Timer", timeout=5)
        except Exception:
            pass

    def test_session_alert(self, session_name):
        if self.sound_settings.get(session_name) != "None":
            self._play_session_sound(session_name)
        if self.show_notifications:
            try:
                from plyer import notification
                message = self.notification_message.replace("{session}", session_name)
                notification.notify(title=self.notification_title, message=message, app_name="Pomodoro Timer", timeout=5)
            except Exception:
                pass

    def start_timer(self):
        if self.is_running:
            return

        self.is_running = True
        self.is_paused = False
        self.start_button.configure(state="disabled")
        if self.include_pause and self.pause_button:
            self.pause_button.configure(state="normal", text="Pause")
        if self.include_skip and self.skip_button:
            self.skip_button.configure(state="normal")
        self.reps += 1

        if self.reps % 8 == 0:
            self.remaining_count = self.long_break_min * 60
            self.title_label.configure(text="Long Break", text_color="#e7305b")
            message_text = self.long_break_message
        elif self.reps % 2 == 0:
            self.remaining_count = self.short_break_min * 60
            self.title_label.configure(text="Short Break", text_color="#e2979c")
            message_text = self.short_break_message
        else:
            self.remaining_count = self.work_min * 60
            self.title_label.configure(text="Work", text_color="#9bdeac")
            message_text = self.work_message

        self.message_label.configure(text=message_text)
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

    def skip_session(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
            
        session_name = self.title_label.cget("text")
        
        # --- NEW: Log skipped sessions as incomplete ---
        duration = self.work_min if session_name == "Work" else (
            self.short_break_min if session_name == "Short Break" else self.long_break_min
        )
        self.history.add_session(session_name, duration, completed=False)
        
        self.is_paused = False
        self.is_running = False
        
        if self.include_pause and self.pause_button:
            self.pause_button.configure(state="disabled", text="Pause")
        if self.include_skip and self.skip_button:
            self.skip_button.configure(state="disabled")

        # Advance to next cycle without extra repetition count adjustment
        next_reps = self.reps + 1
        if next_reps % 8 == 0:
            self.remaining_count = self.long_break_min * 60
            self.title_label.configure(text="Long Break", text_color="#e7305b")
            message_text = self.long_break_message
        elif next_reps % 2 == 0:
            self.remaining_count = self.short_break_min * 60
            self.title_label.configure(text="Short Break", text_color="#e2979c")
            message_text = self.short_break_message
        else:
            self.remaining_count = self.work_min * 60
            self.title_label.configure(text="Work", text_color="#9bdeac")
            message_text = self.work_message

        self.reps = next_reps
        self.message_label.configure(text=message_text)
        self.start_button.configure(state="disabled")
        self.is_running = True
        self.count_down(self.remaining_count)

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
            self.timer_id = None
            session_name = self.title_label.cget("text")
            
            # --- NEW: Record History and Tasks ---
            duration = self.work_min if session_name == "Work" else (
                self.short_break_min if session_name == "Short Break" else self.long_break_min
            )
            self.history.add_session(session_name, duration, completed=True)
            
            if session_name == "Work" and getattr(self, "current_task_id", None):
                self.task_store.update(self.current_task_id, completed=True)
                self.current_task_id = None
                
                # Refresh scheduler GUI if open
                if hasattr(self, "scheduler_panel") and self.scheduler_panel.visible:
                    self.scheduler_panel.refresh()
            # -------------------------------------
            
            self.play_session_alert(session_name)
            marks = "✔" * (self.reps // 2)
            self.check_marks.configure(text=marks)
            
            self.is_running = False
            
            if self.include_pause and self.pause_button:
                self.pause_button.configure(state="disabled", text="Pause")
            if self.include_skip and self.skip_button:
                self.skip_button.configure(state="disabled")
            self.start_button.configure(state="normal")