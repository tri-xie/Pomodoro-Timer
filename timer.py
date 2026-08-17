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
from themes import ThemeManager
from theme_customizer import ThemeCustomizer
from stats import StatsPanel


class PomodoroTimer:

    def __init__(
        self,
        root,
        include_pause=config.INCLUDE_PAUSE_BUTTON
    ):
        self.root = root

        self.app_icon_path = os.path.join(
            os.path.dirname(__file__),
            "app logo.ico"
        )

        # ==================================================
        # LOAD USER SETTINGS
        # ==================================================

        user_settings = config.load_user_settings()

        # ==================================================
        # THEME SYSTEM
        # ==================================================

        self.theme_manager = ThemeManager(
            config.THEME_PATH
        )

        saved_mode = user_settings.get(
            "appearance_mode",
            self.theme_manager.get_mode()
        )

        if saved_mode in (
            "Light",
            "Dark",
            "System"
        ):
            self.theme_manager.set_mode(
                saved_mode
            )

        ctk.set_appearance_mode(
            self.theme_manager.ctk_mode()
        )

        self.palette = self.theme_manager.resolve(
            ctk.get_appearance_mode()
        )

        self.appearance_mode = self.palette["MODE"]
        self.theme = self.palette["PRESET"]

        # ==================================================
        # TIMER SETTINGS
        # ==================================================

        self.include_pause = user_settings.get(
            "include_pause",
            include_pause
        )

        self.include_skip = user_settings.get(
            "include_skip",
            config.INCLUDE_SKIP_BUTTON
        )

        self.work_min = user_settings.get(
            "work_min",
            config.WORK_MIN
        )

        self.short_break_min = user_settings.get(
            "short_break_min",
            config.SHORT_BREAK_MIN
        )

        self.long_break_min = user_settings.get(
            "long_break_min",
            config.LONG_BREAK_MIN
        )

        self.work_message = user_settings.get(
            "work_message",
            config.DEFAULT_SETTINGS["work_message"]
        )

        self.short_break_message = user_settings.get(
            "short_break_message",
            config.DEFAULT_SETTINGS["short_break_message"]
        )

        self.long_break_message = user_settings.get(
            "long_break_message",
            config.DEFAULT_SETTINGS["long_break_message"]
        )

        self.app_font_family = user_settings.get(
            "app_font_family",
            config.DEFAULT_SETTINGS["app_font_family"]
        )

        self.message_font_family = user_settings.get(
            "message_font_family",
            config.DEFAULT_SETTINGS["message_font_family"]
        )

        # ==================================================
        # ALERT SETTINGS
        # ==================================================

        self.enable_session_alerts = user_settings.get(
            "enable_session_alerts",
            config.ENABLE_SESSION_ALERTS
        )

        self.alert_volume = user_settings.get(
            "alert_volume",
            config.ALERT_VOLUME
        )

        self.show_notifications = user_settings.get(
            "show_notifications",
            config.SHOW_NOTIFICATIONS
        )

        self.notification_title = user_settings.get(
            "notification_title",
            config.NOTIFICATION_TITLE
        )

        self.notification_message = user_settings.get(
            "notification_message",
            config.NOTIFICATION_MESSAGE
        )

        # ==================================================
        # SOUND SETTINGS
        # ==================================================

        self.sound_settings = {
            "Work": user_settings.get(
                "work_sound",
                config.WORK_SOUND
            ),

            "Short Break": user_settings.get(
                "short_break_sound",
                config.SHORT_BREAK_SOUND
            ),

            "Long Break": user_settings.get(
                "long_break_sound",
                config.LONG_BREAK_SOUND
            ),
        }

        self.custom_sound_paths = {
            "Work": user_settings.get(
                "work_custom_sound",
                config.WORK_CUSTOM_SOUND
            ),

            "Short Break": user_settings.get(
                "short_break_custom_sound",
                config.SHORT_BREAK_CUSTOM_SOUND
            ),

            "Long Break": user_settings.get(
                "long_break_custom_sound",
                config.LONG_BREAK_CUSTOM_SOUND
            ),
        }

        # ==================================================
        # WINDOW
        # ==================================================

        self.root.title(
            "Pomodoro Timer"
        )

        self.root.configure(
            padx=20,
            pady=20,
            bg=self.palette["APP_BG"]
        )

        self.root.grid_columnconfigure(
            0,
            weight=0
        )

        self.root.grid_columnconfigure(
            1,
            weight=1
        )

        self.root.grid_columnconfigure(
            2,
            weight=0
        )

        # ==================================================
        # TIMER STATE
        # ==================================================

        self.reps = 0
        self.timer_id = None

        self.is_running = False
        self.is_paused = False

        self.remaining_count = (
            self.work_min * 60
        )

        self.current_task_id = None

        # ==================================================
        # BUTTON STATE
        # ==================================================

        self.pause_button = None
        self.skip_button = None

        self.pause_option_var = tk.BooleanVar(
            value=self.include_pause
        )

        self.skip_option_var = tk.BooleanVar(
            value=self.include_skip
        )

        # ==================================================
        # DATA STORES
        # ==================================================

        self.history = SessionHistory(
            config.HISTORY_PATH
        )

        self.task_store = TaskStore(
            config.TASKS_PATH
        )

        # ==================================================
        # BACKGROUND IMAGE STATE
        # ==================================================

        self._background_image_ref = None
        self._background_resize_job = None
        self.background_label = None

        # ==================================================
        # MAIN TITLE
        # ==================================================

        self.title_label = ctk.CTkLabel(
            self.root,
            text="Timer",
            text_color=self.palette["TEXT_COLOR"],
            bg_color=self.palette["APP_BG"],
            font=(
                self.app_font_family,
                35,
                "bold"
            )
        )

        self.title_label.grid(
            column=1,
            row=1,
            pady=(10, 0)
        )

        # ==================================================
        # TIMER CANVAS
        # ==================================================

        self.canvas = tk.Canvas(
            self.root,
            width=200,
            height=224,
            bg=self.palette["CANVAS_BG"],
            highlightthickness=0
        )

        self.time_font = tkfont.Font(
            family=self.app_font_family,
            size=35,
            weight="bold"
        )

        self.time_text = self.canvas.create_text(
            100,
            112,
            text=f"{self.work_min:02d}:00",
            fill=self.palette["TEXT_COLOR"],
            font=self.time_font
        )

        self.canvas.grid(
            column=1,
            row=2,
            pady=20
        )

        # ==================================================
        # MESSAGE
        # ==================================================

        self.message_label = ctk.CTkLabel(
            self.root,
            text=self.work_message,
            text_color=self.palette["TEXT_COLOR"],
            bg_color=self.palette["APP_BG"],
            font=(
                self.message_font_family,
                16
            )
        )

        self.message_label.grid(
            column=1,
            row=3,
            pady=(0, 8)
        )

        # ==================================================
        # TIMER BUTTON FRAME
        # ==================================================

        self.button_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.palette["APP_BG"],
            corner_radius=0
        )

        self.button_frame.grid(
            column=1,
            row=4,
            pady=(0, 10),
            sticky="ew"
        )

        # ==================================================
        # TIMER BUTTONS
        # ==================================================

        self.start_button = ctk.CTkButton(
            self.button_frame,
            text="Start",
            command=self.start_timer,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )

        self.reset_button = ctk.CTkButton(
            self.button_frame,
            text="Reset",
            command=self.reset_timer,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )

        if self.include_pause:
            self.create_pause_button()

        if self.include_skip:
            self.create_skip_button()

        self._update_button_layout()

        # ==================================================
        # TOP ACTIONS
        # ==================================================

        self.top_actions_frame = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )

        self.top_actions_frame.grid(
            column=1,
            row=0,
            pady=(10, 0)
        )

        self.top_actions_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.top_actions_frame.grid_columnconfigure(
            1,
            weight=1
        )

        self.stats_button = ctk.CTkButton(
            self.top_actions_frame,
            text="Session Stats",
            command=self.toggle_stats_panel,
            fg_color=self.palette["BUTTON_BG"],
            hover_color=self.palette["BUTTON_BG"],
            text_color=self.palette["TEXT_COLOR"],
            width=130,
            height=34,
            corner_radius=17
        )

        self.stats_button.grid(
            column=0,
            row=0,
            padx=(0, 4),
            sticky="ew"
        )

        self.schedule_button = ctk.CTkButton(
            self.top_actions_frame,
            text="Schedule Focus",
            command=self.toggle_scheduler_panel,
            fg_color=self.palette["BUTTON_BG"],
            hover_color=self.palette["BUTTON_BG"],
            text_color=self.palette["TEXT_COLOR"],
            width=130,
            height=34,
            corner_radius=17
        )

        self.schedule_button.grid(
            column=1,
            row=0,
            padx=(4, 0),
            sticky="ew"
        )

        # ==================================================
        # SETTINGS BUTTON
        # ==================================================

        self.menu_button = ctk.CTkButton(
            self.root,
            text="⚙",
            command=self.toggle_settings_panel,
            fg_color=self.palette["BUTTON_BG"],
            hover_color=self.palette["BUTTON_BG"],
            text_color=self.palette["TEXT_COLOR"],
            width=60,
            height=40,
            corner_radius=20
        )

        self.menu_button.grid(
            column=0,
            row=0,
            padx=(10, 0),
            pady=(10, 0),
            sticky="w"
        )

        # ==================================================
        # CHECK MARKS
        # ==================================================

        self.check_marks = ctk.CTkLabel(
            self.root,
            text="",
            text_color=self.palette["TEXT_COLOR"],
            bg_color=self.palette["APP_BG"],
            font=(
                self.app_font_family,
                18
            )
        )

        self.check_marks.grid(
            column=1,
            row=5,
            pady=(16, 0)
        )

        # ==================================================
        # PANELS
        # ==================================================

        self.settings_panel = SettingsPanel(
            self.root,
            self
        )

        self.stats_panel = StatsPanel(
            self.root,
            self
        )

        self.scheduler_panel = SchedulerPanel(
            self.root,
            self
        )

        self.theme_customizer = ThemeCustomizer(
            self.root,
            self
        )

        # ==================================================
        # FINAL INITIALIZATION
        # ==================================================

        self.apply_fonts()
        self.apply_theme()

        self.root.bind(
            "<Configure>",
            self._on_window_resize
        )

    # ======================================================
    # SESSION HELPERS
    # ======================================================

    def get_session_name(self):

        if self.reps == 0:
            return "Work"

        if self.reps % 8 == 0:
            return "Long Break"

        if self.reps % 2 == 0:
            return "Short Break"

        return "Work"

    def get_session_duration(
        self,
        session_name
    ):

        if session_name == "Work":
            return self.work_min

        if session_name == "Short Break":
            return self.short_break_min

        if session_name == "Long Break":
            return self.long_break_min

        return self.work_min

    def get_session_message(
        self,
        session_name
    ):

        if session_name == "Work":
            return self.work_message

        if session_name == "Short Break":
            return self.short_break_message

        if session_name == "Long Break":
            return self.long_break_message

        return self.work_message

    def prepare_session(
        self,
        session_name
    ):

        duration = self.get_session_duration(
            session_name
        )

        self.remaining_count = duration * 60

        self.title_label.configure(
            text=session_name,
            text_color=self.palette["TEXT_COLOR"]
        )

        self.message_label.configure(
            text=self.get_session_message(
                session_name
            )
        )

        minutes = (
            self.remaining_count // 60
        )

        seconds = (
            self.remaining_count % 60
        )

        self.canvas.itemconfig(
            self.time_text,
            text=f"{minutes:02d}:{seconds:02d}"
        )

    def start_next_session(self):

        self.reps += 1

        session_name = self.get_session_name()

        self.prepare_session(
            session_name
        )

        return session_name

    # ======================================================
    # RESET TIMER
    # ======================================================

    def reset_timer(self):

        if self.timer_id:

            self.root.after_cancel(
                self.timer_id
            )

            self.timer_id = None

        self.reps = 0
        self.is_running = False
        self.is_paused = False
        self.current_task_id = None

        self.remaining_count = (
            self.work_min * 60
        )

        self.canvas.itemconfig(
            self.time_text,
            text=f"{self.work_min:02d}:00"
        )

        self.title_label.configure(
            text="Timer",
            text_color=self.palette["TEXT_COLOR"]
        )

        self.check_marks.configure(
            text=""
        )

        self.message_label.configure(
            text=self.work_message
        )

        self.start_button.configure(
            state="normal"
        )

        if (
            self.include_pause
            and self.pause_button
        ):

            self.pause_button.configure(
                state="disabled",
                text="Pause"
            )

        if (
            self.include_skip
            and self.skip_button
        ):

            self.skip_button.configure(
                state="disabled"
            )

    # ======================================================
    # PAUSE BUTTON
    # ======================================================

    def create_pause_button(self):

        if self.pause_button:
            return

        self.pause_button = ctk.CTkButton(
            self.button_frame,
            text="Pause",
            command=self.toggle_pause,
            fg_color="#f39c12",
            hover_color="#d68910",
            state="disabled"
        )

        self._update_button_layout()

    # ======================================================
    # SKIP BUTTON
    # ======================================================

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

    # ======================================================
    # BUTTON LAYOUT
    # ======================================================

    def _configure_button_frame_columns(self):

        active_count = (
            2
            + int(self.pause_button is not None)
            + int(self.skip_button is not None)
        )

        for i in range(4):

            self.button_frame.grid_columnconfigure(
                i,
                weight=0,
                minsize=0,
                uniform=""
            )

        for i in range(active_count):

            self.button_frame.grid_columnconfigure(
                i,
                weight=1,
                minsize=0,
                uniform="active_timer_controls"
            )

    def _update_button_layout(self):

        self._configure_button_frame_columns()

        self.start_button.grid_forget()

        if self.pause_button:
            self.pause_button.grid_forget()

        if self.skip_button:
            self.skip_button.grid_forget()

        self.reset_button.grid_forget()

        active = [
            self.start_button
        ]

        if self.pause_button:
            active.append(
                self.pause_button
            )

        if self.skip_button:
            active.append(
                self.skip_button
            )

        active.append(
            self.reset_button
        )

        for column, button in enumerate(active):

            button.grid(
                column=column,
                row=0,
                padx=4,
                pady=5,
                sticky="ew"
            )

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

        self.include_pause = (
            self.pause_option_var.get()
        )

        if self.include_pause:

            self.create_pause_button()

            if self.pause_button:

                self.pause_button.configure(
                    state=(
                        "normal"
                        if self.is_running
                        else "disabled"
                    )
                )

        else:

            self.destroy_pause_button()

        self._update_button_layout()

    def toggle_skip_option(self):

        self.include_skip = (
            self.skip_option_var.get()
        )

        if self.include_skip:

            self.create_skip_button()

            if self.skip_button:

                self.skip_button.configure(
                    state=(
                        "normal"
                        if self.is_running
                        else "disabled"
                    )
                )

        else:

            self.destroy_skip_button()

        self._update_button_layout()

    # ======================================================
    # SETTINGS
    # ======================================================

    def toggle_settings_panel(self):

        if self.settings_panel is None:

            self.settings_panel = SettingsPanel(
                self.root,
                self
            )

        self.settings_panel.toggle()

    # ======================================================
    # FONTS
    # ======================================================

    def apply_fonts(self):

        self.time_font.configure(
            family=self.app_font_family
        )

        self.title_label.configure(
            font=(
                self.app_font_family,
                35,
                "bold"
            )
        )

        self.message_label.configure(
            font=(
                self.message_font_family,
                16
            )
        )

        self.menu_button.configure(
            font=(
                self.app_font_family,
                16,
                "bold"
            )
        )

        self.start_button.configure(
            font=(
                self.app_font_family,
                14,
                "bold"
            )
        )

        self.reset_button.configure(
            font=(
                self.app_font_family,
                14,
                "bold"
            )
        )

        if self.pause_button:

            self.pause_button.configure(
                font=(
                    self.app_font_family,
                    14,
                    "bold"
                )
            )

        if self.skip_button:

            self.skip_button.configure(
                font=(
                    self.app_font_family,
                    14,
                    "bold"
                )
            )

        self.check_marks.configure(
            font=(
                self.app_font_family,
                18
            )
        )

    # ======================================================
    # CHILD WINDOW HELPER
    # ======================================================

    def _prepare_child_window(
        self,
        attr_name,
        title=None
    ):

        existing = getattr(
            self,
            attr_name,
            None
        )

        try:

            if (
                existing is not None
                and existing.winfo_exists()
            ):

                existing.lift()
                existing.focus_force()

                return existing

        except Exception:
            pass

        return None

    # ======================================================
    # BACKGROUND IMAGE
    # ======================================================

    def _clear_background_image(self):

        if self.background_label is not None:

            try:
                self.background_label.destroy()

            except Exception:
                pass

        self.background_label = None
        self._background_image_ref = None

    def _apply_background_image(
        self,
        image_path
    ):

        self._clear_background_image()

        if not image_path:
            return

        if not os.path.isfile(image_path):
            return

        try:

            self.root.update_idletasks()

            width = max(
                self.root.winfo_width(),
                700
            )

            height = max(
                self.root.winfo_height(),
                600
            )

            image = Image.open(
                image_path
            ).convert(
                "RGB"
            )

            image = image.resize(
                (width, height),
                Image.LANCZOS
            )

            self._background_image_ref = (
                ImageTk.PhotoImage(
                    image
                )
            )

            self.background_label = tk.Label(
                self.root,
                image=self._background_image_ref,
                borderwidth=0,
                highlightthickness=0
            )

            self.background_label.place(
                x=0,
                y=0,
                relwidth=1,
                relheight=1
            )

            self.background_label.lower()

        except Exception as error:

            print(
                "Could not load background image:",
                error
            )

            self._background_image_ref = None

    def _on_window_resize(
        self,
        event
    ):

        if event.widget != self.root:
            return

        if self._background_resize_job is not None:

            try:

                self.root.after_cancel(
                    self._background_resize_job
                )

            except Exception:
                pass

        self._background_resize_job = (
            self.root.after(
                150,
                self._resize_background_image
            )
        )

    def _resize_background_image(self):

        self._background_resize_job = None

        if (
            self.theme_manager.get_mode()
            != "Custom"
        ):
            return

        image_path = (
            self.theme_manager.get_background_image()
        )

        if image_path:

            self._apply_background_image(
                image_path
            )

    # ======================================================
    # THEME SYSTEM
    # ======================================================

    def clear_custom_theme(self):

        self._clear_background_image()

    def set_standard_appearance_mode(
        self,
        mode
    ):

        if mode not in (
            "Light",
            "Dark",
            "System"
        ):

            mode = "System"

        self.theme_manager.set_mode(
            mode
        )

        self.appearance_mode = mode

        self._clear_background_image()

        self.apply_theme()

    def apply_custom_theme(self):

        self.apply_theme()

    def apply_theme(self):

        ctk.set_appearance_mode(
            self.theme_manager.ctk_mode()
        )

        self.palette = (
            self.theme_manager.resolve(
                ctk.get_appearance_mode()
            )
        )

        self.appearance_mode = (
            self.palette["MODE"]
        )

        self.theme = (
            self.palette["PRESET"]
        )

        app_bg = self.palette["APP_BG"]
        canvas_bg = self.palette["CANVAS_BG"]
        text_color = self.palette["TEXT_COLOR"]
        button_bg = self.palette["BUTTON_BG"]

        is_custom = self.palette.get(
            "IS_CUSTOM",
            False
        )

        try:

            self.root.configure(
                bg=app_bg
            )

        except Exception:
            pass

        for widget_name in (
            "title_label",
            "message_label",
            "check_marks"
        ):

            widget = getattr(
                self,
                widget_name,
                None
            )

            if widget is not None:

                try:

                    widget.configure(
                        bg_color=app_bg,
                        text_color=text_color
                    )

                except Exception:
                    pass

        if getattr(
            self,
            "canvas",
            None
        ) is not None:

            self.canvas.configure(
                bg=canvas_bg
            )

            self.canvas.itemconfig(
                self.time_text,
                fill=text_color
            )

        if getattr(
            self,
            "button_frame",
            None
        ) is not None:

            self.button_frame.configure(
                fg_color=app_bg
            )

        for button_name in (
            "stats_button",
            "schedule_button",
            "menu_button"
        ):

            button = getattr(
                self,
                button_name,
                None
            )

            if button is not None:

                try:

                    button.configure(
                        fg_color=button_bg,
                        hover_color=button_bg,
                        text_color=text_color
                    )

                except Exception:
                    pass

        if is_custom:

            for button_name in (
                "start_button",
                "pause_button",
                "skip_button",
                "reset_button"
            ):

                button = getattr(
                    self,
                    button_name,
                    None
                )

                if button is not None:

                    try:

                        button.configure(
                            fg_color=button_bg,
                            hover_color=button_bg,
                            text_color=text_color
                        )

                    except Exception:
                        pass

        else:

            self.start_button.configure(
                fg_color="#2ecc71",
                hover_color="#27ae60",
                text_color=text_color
            )

            self.reset_button.configure(
                fg_color="#e74c3c",
                hover_color="#c0392b",
                text_color=text_color
            )

            if self.pause_button:

                self.pause_button.configure(
                    fg_color="#f39c12",
                    hover_color="#d68910",
                    text_color=text_color
                )

            if self.skip_button:

                self.skip_button.configure(
                    fg_color="#3498db",
                    hover_color="#2980b9",
                    text_color=text_color
                )

        if is_custom:

            image_path = self.palette.get(
                "BACKGROUND_IMAGE",
                ""
            )

            if image_path:

                self._apply_background_image(
                    image_path
                )

            else:

                self._clear_background_image()

        else:

            self._clear_background_image()

        for panel_name in (
            "settings_panel",
            "stats_panel",
            "scheduler_panel"
        ):

            panel = getattr(
                self,
                panel_name,
                None
            )

            if (
                panel is not None
                and hasattr(
                    panel,
                    "refresh_theme"
                )
            ):

                try:

                    panel.refresh_theme()

                except Exception:
                    pass

    # ======================================================
    # THEME CUSTOMIZER
    # ======================================================

    def toggle_theme_customizer(self):

        if self.theme_customizer.visible:

            self.theme_customizer.hide()

        else:

            self.theme_customizer.show()

    # ======================================================
    # SCHEDULER
    # ======================================================

    def start_scheduled_task(
        self,
        task
    ):

        self.current_task_id = task.get(
            "id"
        )

        title = task.get(
            "title",
            "Focus Session"
        )

        minutes = int(
            task.get(
                "duration_minutes",
                self.work_min
            )
        )

        self.work_min = minutes

        self.reset_timer()

        self.current_task_id = task.get(
            "id"
        )

        self.message_label.configure(
            text=title
        )

        self.start_timer()

    def toggle_scheduler_panel(self):

        if self.scheduler_panel.visible:

            self.scheduler_panel.hide()

        else:

            self.scheduler_panel.show()

    # ======================================================
    # STATS
    # ======================================================

    def toggle_stats_panel(self):

        if self.stats_panel.visible:

            self.stats_panel.hide()

        else:

            self.stats_panel.show()

    # ======================================================
    # SAVE SETTINGS
    # ======================================================

    def save_settings(self):

        config.save_user_settings({

            "appearance_mode":
                self.theme_manager.get_mode(),

            "work_min":
                self.work_min,

            "short_break_min":
                self.short_break_min,

            "long_break_min":
                self.long_break_min,

            "work_message":
                self.work_message,

            "short_break_message":
                self.short_break_message,

            "long_break_message":
                self.long_break_message,

            "app_font_family":
                self.app_font_family,

            "message_font_family":
                self.message_font_family,

            "include_pause":
                self.include_pause,

            "include_skip":
                self.include_skip,

            "enable_session_alerts":
                self.enable_session_alerts,

            "alert_volume":
                self.alert_volume,

            "show_notifications":
                self.show_notifications,

            "notification_title":
                self.notification_title,

            "notification_message":
                self.notification_message,

            "work_sound":
                self.sound_settings["Work"],

            "short_break_sound":
                self.sound_settings["Short Break"],

            "long_break_sound":
                self.sound_settings["Long Break"],

            "work_custom_sound":
                self.custom_sound_paths["Work"],

            "short_break_custom_sound":
                self.custom_sound_paths[
                    "Short Break"
                ],

            "long_break_custom_sound":
                self.custom_sound_paths[
                    "Long Break"
                ],
        })

    # ======================================================
    # SESSION SOUNDS
    # ======================================================

    def _play_custom_wav(
        self,
        path,
        volume
    ):

        if (
            not path
            or not os.path.isfile(path)
        ):

            return False

        try:

            import pygame

            if not pygame.mixer.get_init():

                pygame.mixer.init()

            sound = pygame.mixer.Sound(
                path
            )

            sound.set_volume(
                max(
                    0,
                    min(
                        100,
                        volume
                    )
                )
                / 100.0
            )

            sound.play()

            return True

        except Exception:

            return False

    def _play_session_sound(
        self,
        session_name
    ):

        choice = self.sound_settings.get(
            session_name,
            "System Default"
        )

        if choice == "None":

            return

        if (
            choice == "Custom"
            and self._play_custom_wav(
                self.custom_sound_paths.get(
                    session_name,
                    ""
                ),
                self.alert_volume
            )
        ):

            return

        try:

            if sys.platform.startswith(
                "win"
            ):

                import winsound

                sounds = {
                    "System Default":
                        winsound.MB_OK,

                    "Information":
                        winsound.MB_ICONASTERISK,

                    "Warning":
                        winsound.MB_ICONEXCLAMATION,

                    "Error":
                        winsound.MB_ICONHAND,
                }

                winsound.MessageBeep(
                    sounds.get(
                        choice,
                        winsound.MB_OK
                    )
                )

            elif sys.platform == "darwin":

                sound_file = {
                    "System Default":
                        "/System/Library/Sounds/Glass.aiff",

                    "Information":
                        "/System/Library/Sounds/Ping.aiff",

                    "Warning":
                        "/System/Library/Sounds/Basso.aiff",

                    "Error":
                        "/System/Library/Sounds/Sosumi.aiff",
                }.get(
                    choice,
                    "/System/Library/Sounds/Glass.aiff"
                )

                subprocess.Popen(
                    [
                        "afplay",
                        "-v",
                        str(
                            self.alert_volume / 100
                        ),
                        sound_file
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            else:

                self.root.bell()

        except Exception:

            try:

                self.root.bell()

            except Exception:
                pass

    def play_session_alert(
        self,
        session_name
    ):

        if not self.enable_session_alerts:

            return

        self._play_session_sound(
            session_name
        )

        if not self.show_notifications:

            return

        try:

            from plyer import notification

            message = (
                self.notification_message.replace(
                    "{session}",
                    session_name
                )
            )

            notification.notify(
                title=self.notification_title,
                message=message,
                app_name="Pomodoro Timer",
                timeout=5
            )

        except Exception:
            pass

    def test_session_alert(
        self,
        session_name
    ):

        if (
            self.sound_settings.get(
                session_name
            )
            != "None"
        ):

            self._play_session_sound(
                session_name
            )

        if self.show_notifications:

            try:

                from plyer import notification

                message = (
                    self.notification_message.replace(
                        "{session}",
                        session_name
                    )
                )

                notification.notify(
                    title=self.notification_title,
                    message=message,
                    app_name="Pomodoro Timer",
                    timeout=5
                )

            except Exception:
                pass

    # ======================================================
    # TIMER LOGIC
    # ======================================================

    def start_timer(self):

        if self.is_running:
            return

        # Resume an existing paused session.
        if self.is_paused:

            self.is_paused = False
            self.is_running = True

            self.start_button.configure(
                state="disabled"
            )

            if (
                self.include_pause
                and self.pause_button
            ):

                self.pause_button.configure(
                    state="normal",
                    text="Pause"
                )

            if (
                self.include_skip
                and self.skip_button
            ):

                self.skip_button.configure(
                    state="normal"
                )

            self.count_down(
                self.remaining_count
            )

            return

        self.is_running = True
        self.is_paused = False

        self.start_button.configure(
            state="disabled"
        )

        if (
            self.include_pause
            and self.pause_button
        ):

            self.pause_button.configure(
                state="normal",
                text="Pause"
            )

        if (
            self.include_skip
            and self.skip_button
        ):

            self.skip_button.configure(
                state="normal"
            )

        self.start_next_session()

        self.count_down(
            self.remaining_count
        )

    # ======================================================
    # PAUSE / RESUME
    # ======================================================

    def toggle_pause(self):

        if (
            not self.is_running
            and not self.is_paused
        ):
            return

        # Resume
        if self.is_paused:

            self.is_paused = False
            self.is_running = True

            if self.pause_button:

                self.pause_button.configure(
                    text="Pause"
                )

            self.count_down(
                self.remaining_count
            )

            return

        # Pause
        if self.timer_id:

            self.root.after_cancel(
                self.timer_id
            )

            self.timer_id = None

        self.is_paused = True
        self.is_running = False

        if self.pause_button:

            self.pause_button.configure(
                text="Resume"
            )

    # ======================================================
    # SKIP SESSION
    # ======================================================

    def skip_session(self):

        if not (
            self.is_running
            or self.is_paused
        ):
            return

        if self.timer_id:

            self.root.after_cancel(
                self.timer_id
            )

            self.timer_id = None

        session_name = self.get_session_name()

        duration = self.get_session_duration(
            session_name
        )

        # Record skipped session.
        self.history.add_session(
            session_name,
            duration,
            completed=False
        )

        self.is_paused = False
        self.is_running = True

        if (
            self.include_pause
            and self.pause_button
        ):

            self.pause_button.configure(
                state="normal",
                text="Pause"
            )

        if (
            self.include_skip
            and self.skip_button
        ):

            self.skip_button.configure(
                state="normal"
            )

        # Start next session.
        self.start_next_session()

        self.count_down(
            self.remaining_count
        )

    # ======================================================
    # COUNTDOWN
    # ======================================================

    def count_down(
        self,
        count
    ):

        self.remaining_count = count

        minutes = count // 60
        seconds = count % 60

        self.canvas.itemconfig(
            self.time_text,
            text=f"{minutes:02d}:{seconds:02d}"
        )

        # Continue countdown.
        if (
            count > 0
            and self.is_running
        ):

            self.timer_id = self.root.after(
                1000,
                self.count_down,
                count - 1
            )

            return

        # Session is not finished.
        if count != 0:
            return

        self.timer_id = None

        session_name = self.get_session_name()

        duration = self.get_session_duration(
            session_name
        )

        # Record completed session.
        self.history.add_session(
            session_name,
            duration,
            completed=True
        )

        # Complete scheduled task after Work session.
        if (
            session_name == "Work"
            and getattr(
                self,
                "current_task_id",
                None
            )
        ):

            self.task_store.update(
                self.current_task_id,
                completed=True
            )

            self.current_task_id = None

            if (
                hasattr(
                    self,
                    "scheduler_panel"
                )
                and self.scheduler_panel.visible
            ):

                self.scheduler_panel.refresh()

        # Play the correct alert.
        self.play_session_alert(
            session_name
        )

        # Add a check mark only for completed Work sessions.
        if session_name == "Work":

            completed_work_sessions = (
                (self.reps + 1) // 2
            )

            self.check_marks.configure(
                text="✔" * completed_work_sessions
            )

        # Stop current session.
        self.is_running = False
        self.is_paused = False

        self.start_button.configure(
            state="normal"
        )

        if (
            self.include_pause
            and self.pause_button
        ):

            self.pause_button.configure(
                state="disabled",
                text="Pause"
            )

        if (
            self.include_skip
            and self.skip_button
        ):

            self.skip_button.configure(
                state="disabled"
            )