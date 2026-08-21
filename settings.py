import os
import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk

import config


class SettingsPanel:

    def __init__(self, parent, timer):
        self.parent = parent
        self.timer = timer
        self.visible = False

        # --------------------------------------------------
        # PANEL WINDOW
        # --------------------------------------------------

        self.window = ctk.CTkToplevel(parent)

        self.window.title("Settings")
        self.window.geometry("620x700")
        self.window.minsize(560, 600)

        self.window.protocol(
            "WM_DELETE_WINDOW",
            self.hide
        )

        # Start hidden
        self.window.withdraw()

        self.window.grid_columnconfigure(
            0,
            weight=1
        )

        self.window.grid_rowconfigure(
            0,
            weight=1
        )

        self._build_ui()
        self.load_from_timer()
        self.refresh_theme()

    # ==================================================
    # BUILD UI
    # ==================================================

    def _build_ui(self):

        # --------------------------------------------------
        # MAIN SCROLLABLE CONTAINER
        # --------------------------------------------------

        self.scroll = ctk.CTkScrollableFrame(
            self.window,
            corner_radius=0
        )

        self.scroll.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.scroll.grid_columnconfigure(
            0,
            weight=1
        )

        row = 0

        # ==================================================
        # TITLE
        # ==================================================

        self.title_label = ctk.CTkLabel(
            self.scroll,
            text="Settings",
            font=("Helvetica", 28, "bold")
        )

        self.title_label.grid(
            row=row,
            column=0,
            pady=(20, 15)
        )

        row += 1

        # ==================================================
        # TIMER SETTINGS
        # ==================================================

        self.timer_section = self._create_section(
            "Timer Settings"
        )

        self.timer_section.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=20,
            pady=8
        )

        row += 1

        self.work_var = tk.StringVar()
        self.short_break_var = tk.StringVar()
        self.long_break_var = tk.StringVar()

        self._add_entry_row(
            self.timer_section,
            0,
            "Work (minutes)",
            self.work_var
        )

        self._add_entry_row(
            self.timer_section,
            1,
            "Short Break (minutes)",
            self.short_break_var
        )

        self._add_entry_row(
            self.timer_section,
            2,
            "Long Break (minutes)",
            self.long_break_var
        )

        # ==================================================
        # SESSION MESSAGES
        # ==================================================

        self.message_section = self._create_section(
            "Session Messages"
        )

        self.message_section.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=20,
            pady=8
        )

        row += 1

        self.work_message_var = tk.StringVar()
        self.short_break_message_var = tk.StringVar()
        self.long_break_message_var = tk.StringVar()

        self._add_entry_row(
            self.message_section,
            0,
            "Work Message",
            self.work_message_var
        )

        self._add_entry_row(
            self.message_section,
            1,
            "Short Break Message",
            self.short_break_message_var
        )

        self._add_entry_row(
            self.message_section,
            2,
            "Long Break Message",
            self.long_break_message_var
        )

        # ==================================================
        # APPEARANCE
        # ==================================================

        self.appearance_section = self._create_section(
            "Appearance"
        )

        self.appearance_section.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=20,
            pady=8
        )

        row += 1

        appearance_label = ctk.CTkLabel(
            self.appearance_section,
            text="Appearance Mode"
        )

        appearance_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=10,
            pady=6
        )

        self.appearance_var = tk.StringVar()

        appearance_choices = getattr(
            config,
            "APPEARANCE_MODE_CHOICES",
            ["System", "Light", "Dark"]
        )

        self.appearance_menu = ctk.CTkOptionMenu(
            self.appearance_section,
            values=appearance_choices,
            variable=self.appearance_var,
            command=self.change_appearance_mode
        )

        self.appearance_menu.grid(
            row=1,
            column=1,
            columnspan=2,
            sticky="ew",
            padx=10,
            pady=6
        )

        # Custom Theme button
        self.custom_theme_button = ctk.CTkButton(
            self.appearance_section,
            text="Custom Theme",
            command=self.open_custom_theme
        )

        self.custom_theme_button.grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=10,
            pady=(6, 12)
        )

        # ==================================================
        # FONTS
        # ==================================================

        self.font_section = self._create_section(
            "Fonts"
        )

        self.font_section.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=20,
            pady=8
        )

        row += 1

        self.app_font_var = tk.StringVar()
        self.message_font_var = tk.StringVar()

        font_choices = getattr(
            config,
            "APP_FONT_CHOICES",
            [
                "Courier",
                "Helvetica",
                "Times",
                "Arial",
                "Consolas"
            ]
        )

        self._add_option_row(
            self.font_section,
            0,
            "Application Font",
            self.app_font_var,
            font_choices,
            self.change_app_font
        )

        message_font_choices = getattr(
            config,
            "MESSAGE_FONT_CHOICES",
            font_choices
        )

        self._add_option_row(
            self.font_section,
            1,
            "Message Font",
            self.message_font_var,
            message_font_choices,
            self.change_message_font
        )

        # ==================================================
        # TIMER CONTROLS
        # ==================================================

        self.button_section = self._create_section(
            "Timer Controls"
        )

        self.button_section.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=20,
            pady=8
        )

        row += 1

        self.pause_var = self.timer.pause_option_var
        self.skip_var = self.timer.skip_option_var

        self.pause_checkbox = ctk.CTkCheckBox(
            self.button_section,
            text="Show Pause / Resume Button",
            variable=self.pause_var,
            command=self.timer.toggle_pause_option
        )

        self.pause_checkbox.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="w",
            padx=10,
            pady=6
        )

        self.skip_checkbox = ctk.CTkCheckBox(
            self.button_section,
            text="Show Skip Button",
            variable=self.skip_var,
            command=self.timer.toggle_skip_option
        )

        self.skip_checkbox.grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="w",
            padx=10,
            pady=(6, 12)
        )

        # ==================================================
        # SESSION ALERTS
        # ==================================================

        self.alert_section = self._create_section(
            "Session Alerts"
        )

        self.alert_section.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=20,
            pady=8
        )

        row += 1

        self.alerts_enabled_var = tk.BooleanVar()

        self.alerts_checkbox = ctk.CTkCheckBox(
            self.alert_section,
            text="Enable Session Alerts",
            variable=self.alerts_enabled_var,
            command=self.toggle_alerts
        )

        self.alerts_checkbox.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="w",
            padx=10,
            pady=6
        )

        volume_label = ctk.CTkLabel(
            self.alert_section,
            text="Alert Volume"
        )

        volume_label.grid(
            row=2,
            column=0,
            sticky="w",
            padx=10,
            pady=(6, 12)
        )

        self.volume_var = tk.DoubleVar()

        self.volume_slider = ctk.CTkSlider(
            self.alert_section,
            from_=0,
            to=100,
            number_of_steps=100,
            variable=self.volume_var
        )

        self.volume_slider.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=10,
            pady=(6, 12)
        )

        self.volume_value_label = ctk.CTkLabel(
            self.alert_section,
            text="80%"
        )

        self.volume_value_label.grid(
            row=2,
            column=2,
            padx=(0, 10),
            pady=(6, 12)
        )

        self.volume_var.trace_add(
            "write",
            self.update_volume_label
        )

        # ==================================================
        # NOTIFICATIONS
        # ==================================================

        self.notification_section = self._create_section(
            "Notifications"
        )

        self.notification_section.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=20,
            pady=8
        )

        row += 1

        self.notifications_var = tk.BooleanVar()

        self.notifications_checkbox = ctk.CTkCheckBox(
            self.notification_section,
            text="Show Desktop Notifications",
            variable=self.notifications_var
        )

        # Row 1: checkbox
        self.notifications_checkbox.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="w",
            padx=10,
            pady=6
        )

        self.notification_title_var = tk.StringVar()
        self.notification_message_var = tk.StringVar()

        # Row 2: title
        self._add_entry_row(
            self.notification_section,
            1,
            "Notification Title",
            self.notification_title_var
        )

        # Row 3: message
        self._add_entry_row(
            self.notification_section,
            2,
            "Notification Message",
            self.notification_message_var
        )

        # ==================================================
        # SESSION SOUNDS
        # ==================================================

        self.sound_section = self._create_section(
            "Session Sounds"
        )

        self.sound_section.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=20,
            pady=8
        )

        row += 1

        sound_choices = getattr(
            config,
            "SOUND_CHOICES",
            [
                "System Default",
                "Information",
                "Warning",
                "Error",
                "Custom",
                "None"
            ]
        )

        self.sound_vars = {
            "Work": tk.StringVar(),
            "Short Break": tk.StringVar(),
            "Long Break": tk.StringVar()
        }

        self.custom_sound_vars = {
            "Work": tk.StringVar(),
            "Short Break": tk.StringVar(),
            "Long Break": tk.StringVar()
        }

        self.sound_file_labels = {}

        self._add_sound_row(
            self.sound_section,
            1,
            "Work",
            self.sound_vars["Work"],
            sound_choices
        )

        self._add_sound_row(
            self.sound_section,
            4,
            "Short Break",
            self.sound_vars["Short Break"],
            sound_choices
        )

        self._add_sound_row(
            self.sound_section,
            7,
            "Long Break",
            self.sound_vars["Long Break"],
            sound_choices
        )

        # ==================================================
        # SAVE / CLOSE
        # ==================================================

        self.action_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="transparent"
        )

        self.action_frame.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=20,
            pady=(15, 25)
        )

        self.action_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.action_frame.grid_columnconfigure(
            1,
            weight=1
        )

        self.save_button = ctk.CTkButton(
            self.action_frame,
            text="Save Settings",
            command=self.save_settings
        )

        self.save_button.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 5)
        )

        self.close_button = ctk.CTkButton(
            self.action_frame,
            text="Close",
            command=self.hide
        )

        self.close_button.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(5, 0)
        )

    # ==================================================
    # UI HELPERS
    # ==================================================

    def _create_section(self, title):

        frame = ctk.CTkFrame(
            self.scroll,
            corner_radius=12
        )

        frame.grid_columnconfigure(
            0,
            weight=0
        )

        frame.grid_columnconfigure(
            1,
            weight=1
        )

        frame.grid_columnconfigure(
            2,
            weight=0
        )

        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=("Helvetica", 18, "bold")
        )

        title_label.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            padx=10,
            pady=(10, 8)
        )

        frame.section_title = title_label

        return frame

    def _add_entry_row(
        self,
        parent,
        row,
        label_text,
        variable
    ):

        grid_row = row + 1

        label = ctk.CTkLabel(
            parent,
            text=label_text
        )

        label.grid(
            row=grid_row,
            column=0,
            sticky="w",
            padx=10,
            pady=6
        )

        entry = ctk.CTkEntry(
            parent,
            textvariable=variable
        )

        entry.grid(
            row=grid_row,
            column=1,
            columnspan=2,
            sticky="ew",
            padx=10,
            pady=6
        )

        return entry

    def _add_option_row(
        self,
        parent,
        row,
        label_text,
        variable,
        values,
        command=None
    ):

        grid_row = row + 1

        label = ctk.CTkLabel(
            parent,
            text=label_text
        )

        label.grid(
            row=grid_row,
            column=0,
            sticky="w",
            padx=10,
            pady=6
        )

        option_menu = ctk.CTkOptionMenu(
            parent,
            values=values,
            variable=variable,
            command=command
        )

        option_menu.grid(
            row=grid_row,
            column=1,
            columnspan=2,
            sticky="ew",
            padx=10,
            pady=6
        )

        return option_menu

    # ==================================================
    # SOUND ROW
    # ==================================================

    def _add_sound_row(
        self,
        parent,
        row,
        session_name,
        variable,
        choices
    ):

        label = ctk.CTkLabel(
            parent,
            text=f"{session_name} Sound"
        )

        label.grid(
            row=row,
            column=0,
            sticky="w",
            padx=10,
            pady=6
        )

        menu = ctk.CTkOptionMenu(
            parent,
            values=choices,
            variable=variable,
            command=lambda choice,
            name=session_name:
                self.change_sound(
                    name,
                    choice
                )
        )

        menu.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=10,
            pady=6
        )

        test_button = ctk.CTkButton(
            parent,
            text="Test",
            width=80,
            command=lambda name=session_name:
                self.test_selected_sound(
                    name
                )
        )

        test_button.grid(
            row=row,
            column=2,
            sticky="ew",
            padx=(0, 10),
            pady=6
        )

        choose_button = ctk.CTkButton(
            parent,
            text="Choose Sound File",
            command=lambda name=session_name:
                self.choose_custom_sound(
                    name
                )
        )

        choose_button.grid(
            row=row + 1,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=10,
            pady=(0, 4)
        )

        file_label = ctk.CTkLabel(
            parent,
            text="No custom sound selected",
            anchor="w"
        )

        file_label.grid(
            row=row + 2,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=10,
            pady=(0, 10)
        )

        self.sound_file_labels[
            session_name
        ] = file_label

        return menu

    # ==================================================
    # CUSTOM SOUNDS
    # ==================================================

    def change_sound(
        self,
        session_name,
        choice
    ):

        if choice == "Custom":

            current_path = (
                self.custom_sound_vars[
                    session_name
                ].get()
            )

            if not current_path:

                self.choose_custom_sound(
                    session_name
                )

                if not self.custom_sound_vars[
                    session_name
                ].get():

                    self.sound_vars[
                        session_name
                    ].set(
                        "System Default"
                    )

                    self.timer.sound_settings[
                        session_name
                    ] = "System Default"

                    return

            self.timer.sound_settings[
                session_name
            ] = "Custom"

            return

        self.timer.sound_settings[
            session_name
        ] = choice

    def choose_custom_sound(
        self,
        session_name
    ):

        file_path = filedialog.askopenfilename(
            parent=self.window,
            title=f"Choose sound for {session_name}",
            filetypes=[
                (
                    "Audio files",
                    "*.wav *.mp3 *.ogg"
                ),
                (
                    "WAV files",
                    "*.wav"
                ),
                (
                    "MP3 files",
                    "*.mp3"
                ),
                (
                    "OGG files",
                    "*.ogg"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if not file_path:
            return

        self.custom_sound_vars[
            session_name
        ].set(
            file_path
        )

        self.timer.custom_sound_paths[
            session_name
        ] = file_path

        self.sound_vars[
            session_name
        ].set(
            "Custom"
        )

        self.timer.sound_settings[
            session_name
        ] = "Custom"

        file_name = os.path.basename(
            file_path
        )

        self.sound_file_labels[
            session_name
        ].configure(
            text=file_name
        )

    def test_selected_sound(
        self,
        session_name
    ):

        sound_choice = self.sound_vars[
            session_name
        ].get()

        custom_path = self.custom_sound_vars[
            session_name
        ].get()

        if sound_choice == "Custom" and not custom_path:

            self.show_error(
                f"Please choose a custom sound file "
                f"for {session_name} first."
            )

            return

        self.timer.sound_settings[
            session_name
        ] = sound_choice

        self.timer.custom_sound_paths[
            session_name
        ] = custom_path

        self.timer.test_session_alert(
            session_name
        )

    # ==================================================
    # PANEL VISIBILITY
    # ==================================================

    def show(self):

        self.load_from_timer()

        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()

        self.visible = True

    def hide(self):

        self.window.withdraw()

        self.visible = False

    def toggle(self):

        if self.visible:
            self.hide()
        else:
            self.show()

    # ==================================================
    # LOAD CURRENT VALUES
    # ==================================================

    def load_from_timer(self):

        self.work_var.set(
            str(self.timer.work_min)
        )

        self.short_break_var.set(
            str(self.timer.short_break_min)
        )

        self.long_break_var.set(
            str(self.timer.long_break_min)
        )

        self.work_message_var.set(
            self.timer.work_message
        )

        self.short_break_message_var.set(
            self.timer.short_break_message
        )

        self.long_break_message_var.set(
            self.timer.long_break_message
        )

        mode = self.timer.theme_manager.data.get(
            "mode",
            "System"
        )

        if mode not in (
            "System",
            "Light",
            "Dark"
        ):
            mode = "System"

        self.appearance_var.set(
            mode
        )

        self.app_font_var.set(
            self.timer.app_font_family
        )

        self.message_font_var.set(
            self.timer.message_font_family
        )

        self.pause_var.set(
            self.timer.include_pause
        )

        self.skip_var.set(
            self.timer.include_skip
        )

        self.alerts_enabled_var.set(
            self.timer.enable_session_alerts
        )

        self.volume_var.set(
            self.timer.alert_volume
        )

        self.notifications_var.set(
            self.timer.show_notifications
        )

        self.notification_title_var.set(
            self.timer.notification_title
        )

        self.notification_message_var.set(
            self.timer.notification_message
        )

        for session_name in (
            "Work",
            "Short Break",
            "Long Break"
        ):

            sound_choice = (
                self.timer.sound_settings.get(
                    session_name,
                    "System Default"
                )
            )

            custom_path = (
                self.timer.custom_sound_paths.get(
                    session_name,
                    ""
                )
            )

            self.sound_vars[
                session_name
            ].set(
                sound_choice
            )

            self.custom_sound_vars[
                session_name
            ].set(
                custom_path
            )

            if custom_path:

                file_name = os.path.basename(
                    custom_path
                )

            else:

                file_name = (
                    "No custom sound selected"
                )

            self.sound_file_labels[
                session_name
            ].configure(
                text=file_name
            )

        self.update_volume_label()

    # ==================================================
    # APPEARANCE
    # ==================================================

    def change_appearance_mode(
        self,
        mode
    ):

        if mode not in (
            "System",
            "Light",
            "Dark"
        ):
            return

        self.timer.set_standard_appearance_mode(
            mode
        )

        self.refresh_theme()

    def open_custom_theme(self):

        self.timer.toggle_theme_customizer()

    # ==================================================
    # FONT CHANGES
    # ==================================================

    def change_app_font(
        self,
        value
    ):

        self.timer.app_font_family = value

        self.timer.apply_fonts()

    def change_message_font(
        self,
        value
    ):

        self.timer.message_font_family = value

        self.timer.apply_fonts()

    # ==================================================
    # ALERTS
    # ==================================================

    def toggle_alerts(self):

        self.timer.enable_session_alerts = (
            self.alerts_enabled_var.get()
        )

    def update_volume_label(
        self,
        *args
    ):

        try:

            value = int(
                float(
                    self.volume_var.get()
                )
            )

            self.volume_value_label.configure(
                text=f"{value}%"
            )

        except Exception:
            pass

    # ==================================================
    # SAVE SETTINGS
    # ==================================================

    def save_settings(self):

        try:

            work_min = int(
                self.work_var.get()
            )

            short_break_min = int(
                self.short_break_var.get()
            )

            long_break_min = int(
                self.long_break_var.get()
            )

            if (
                work_min <= 0
                or short_break_min <= 0
                or long_break_min <= 0
            ):
                raise ValueError

        except ValueError:

            self.show_error(
                "Please enter valid timer values greater than zero."
            )

            return

        # --------------------------------------------------
        # TIMER VALUES
        # --------------------------------------------------

        self.timer.work_min = work_min
        self.timer.short_break_min = short_break_min
        self.timer.long_break_min = long_break_min

        # --------------------------------------------------
        # MESSAGES
        # --------------------------------------------------

        self.timer.work_message = (
            self.work_message_var.get().strip()
        )

        self.timer.short_break_message = (
            self.short_break_message_var.get().strip()
        )

        self.timer.long_break_message = (
            self.long_break_message_var.get().strip()
        )

        # --------------------------------------------------
        # FONTS
        # --------------------------------------------------

        self.timer.app_font_family = (
            self.app_font_var.get()
        )

        self.timer.message_font_family = (
            self.message_font_var.get()
        )

        # --------------------------------------------------
        # BUTTON OPTIONS
        # --------------------------------------------------

        # The BooleanVars already contain the correct values.
        # Calling these methods updates the actual button layout.

        self.timer.include_pause = (
            self.pause_var.get()
        )

        self.timer.include_skip = (
            self.skip_var.get()
        )

        self.timer.toggle_pause_option()
        self.timer.toggle_skip_option()

        # --------------------------------------------------
        # ALERT SETTINGS
        # --------------------------------------------------

        self.timer.enable_session_alerts = (
            self.alerts_enabled_var.get()
        )

        self.timer.alert_volume = int(
            float(
                self.volume_var.get()
            )
        )

        self.timer.show_notifications = (
            self.notifications_var.get()
        )

        self.timer.notification_title = (
            self.notification_title_var.get().strip()
        )

        self.timer.notification_message = (
            self.notification_message_var.get().strip()
        )

        # --------------------------------------------------
        # SOUND SETTINGS
        # --------------------------------------------------

        for session_name in (
            "Work",
            "Short Break",
            "Long Break"
        ):

            sound_choice = self.sound_vars[
                session_name
            ].get()

            custom_path = self.custom_sound_vars[
                session_name
            ].get()

            if (
                sound_choice == "Custom"
                and not custom_path
            ):

                self.show_error(
                    f"Please choose a custom sound file "
                    f"for {session_name}."
                )

                return

            self.timer.sound_settings[
                session_name
            ] = sound_choice

            self.timer.custom_sound_paths[
                session_name
            ] = custom_path

        # --------------------------------------------------
        # APPLY CHANGES
        # --------------------------------------------------

        self.timer.apply_fonts()

        if not self.timer.is_running:

            self.timer.reset_timer()

        self.timer.save_settings()

        self.show_success(
            "Settings saved successfully."
        )

    # ==================================================
    # MESSAGES
    # ==================================================

    def show_error(
        self,
        message
    ):

        dialog = ctk.CTkToplevel(
            self.window
        )

        dialog.title(
            "Settings Error"
        )

        dialog.geometry(
            "360x160"
        )

        dialog.transient(
            self.window
        )

        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=message,
            wraplength=300
        ).pack(
            padx=20,
            pady=(25, 15)
        )

        ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy
        ).pack(
            pady=(0, 20)
        )

    def show_success(
        self,
        message
    ):

        dialog = ctk.CTkToplevel(
            self.window
        )

        dialog.title(
            "Settings"
        )

        dialog.geometry(
            "360x160"
        )

        dialog.transient(
            self.window
        )

        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=message,
            wraplength=300
        ).pack(
            padx=20,
            pady=(25, 15)
        )

        ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy
        ).pack(
            pady=(0, 20)
        )

    # ==================================================
    # THEME REFRESH
    # ==================================================

    def refresh_theme(self):

        palette = getattr(
            self.timer,
            "palette",
            {}
        )

        app_bg = palette.get(
            "APP_BG",
            "#FFFFFF"
        )

        frame_bg = palette.get(
            "FRAME_BG",
            "#F0F0F0"
        )

        text_color = palette.get(
            "TEXT_COLOR",
            "#000000"
        )

        button_bg = palette.get(
            "BUTTON_BG",
            "#3B8ED0"
        )

        try:

            self.window.configure(
                fg_color=app_bg
            )

        except Exception:
            pass

        try:

            self.scroll.configure(
                fg_color=app_bg
            )

        except Exception:
            pass

        self.title_label.configure(
            text_color=text_color
        )

        sections = (
            self.timer_section,
            self.message_section,
            self.appearance_section,
            self.font_section,
            self.button_section,
            self.alert_section,
            self.notification_section,
            self.sound_section
        )

        for section in sections:

            try:

                section.configure(
                    fg_color=frame_bg
                )

                section.section_title.configure(
                    text_color=text_color
                )

            except Exception:
                pass

        self._refresh_widget_tree(
            self.scroll,
            text_color,
            button_bg
        )

        self.custom_theme_button.configure(
            fg_color=button_bg,
            hover_color=button_bg,
            text_color=text_color
        )

    def _refresh_widget_tree(
        self,
        widget,
        text_color,
        button_bg
    ):

        for child in widget.winfo_children():

            try:

                if isinstance(
                    child,
                    ctk.CTkLabel
                ):

                    child.configure(
                        text_color=text_color
                    )

                elif isinstance(
                    child,
                    ctk.CTkButton
                ):

                    child.configure(
                        text_color=text_color
                    )

                elif isinstance(
                    child,
                    ctk.CTkCheckBox
                ):

                    child.configure(
                        text_color=text_color
                    )

            except Exception:
                pass

            self._refresh_widget_tree(
                child,
                text_color,
                button_bg
            )