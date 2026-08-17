import os
import customtkinter as ctk
from tkinter import filedialog

from themes import CUSTOM_PRESETS


class ThemeCustomizer:
    def __init__(self, parent, timer):
        self.parent = parent
        self.timer = timer
        self.visible = False

        # Temporary background selection.
        # We don't permanently save it until Apply Theme.
        self.selected_background_image = (
            self.timer.theme_manager.get_background_image()
        )

        # ==================================================
        # WINDOW
        # ==================================================

        self.window = ctk.CTkToplevel(parent)

        self.window.title("Custom Themes")
        self.window.geometry("620x560")
        self.window.minsize(540, 500)

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

        self._build_ui()
        self.refresh()

    # ==================================================
    # BUILD UI
    # ==================================================

    def _build_ui(self):

        # --------------------------------------------------
        # MAIN CONTAINER
        # --------------------------------------------------

        self.main_frame = ctk.CTkFrame(
            self.window,
            fg_color="transparent"
        )

        self.main_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=25,
            pady=20
        )

        self.main_frame.grid_columnconfigure(
            0,
            weight=1
        )

        # --------------------------------------------------
        # TITLE
        # --------------------------------------------------

        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Custom Themes",
            font=("Helvetica", 26, "bold")
        )

        self.title_label.grid(
            row=0,
            column=0,
            pady=(5, 5)
        )

        self.subtitle_label = ctk.CTkLabel(
            self.main_frame,
            text=(
                "Choose a color preset and optionally "
                "add a background image."
            ),
            wraplength=500,
            justify="center"
        )

        self.subtitle_label.grid(
            row=1,
            column=0,
            pady=(0, 20)
        )

        # ==================================================
        # PRESET SECTION
        # ==================================================

        self.preset_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=12
        )

        self.preset_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=8
        )

        self.preset_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.preset_title = ctk.CTkLabel(
            self.preset_frame,
            text="Color Preset",
            font=("Helvetica", 18, "bold")
        )

        self.preset_title.grid(
            row=0,
            column=0,
            pady=(12, 8)
        )

        self.choice = ctk.CTkOptionMenu(
            self.preset_frame,
            values=list(CUSTOM_PRESETS.keys()),
            command=self.preview
        )

        self.choice.grid(
            row=1,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="ew"
        )

        # ==================================================
        # PREVIEW
        # ==================================================

        self.preview_box = ctk.CTkFrame(
            self.main_frame,
            height=130,
            corner_radius=12
        )

        self.preview_box.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=12
        )

        self.preview_box.grid_propagate(False)

        self.preview_label = ctk.CTkLabel(
            self.preview_box,
            text="Theme Preview",
            font=("Helvetica", 20, "bold")
        )

        self.preview_label.place(
            relx=0.5,
            rely=0.42,
            anchor="center"
        )

        self.preview_button = ctk.CTkButton(
            self.preview_box,
            text="Sample Button",
            width=150
        )

        self.preview_button.place(
            relx=0.5,
            rely=0.73,
            anchor="center"
        )

        # ==================================================
        # BACKGROUND IMAGE
        # ==================================================

        self.image_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=12
        )

        self.image_frame.grid(
            row=4,
            column=0,
            sticky="ew",
            pady=8
        )

        self.image_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.image_title = ctk.CTkLabel(
            self.image_frame,
            text="Background Image",
            font=("Helvetica", 18, "bold")
        )

        self.image_title.grid(
            row=0,
            column=0,
            pady=(12, 5)
        )

        self.image_status = ctk.CTkLabel(
            self.image_frame,
            text="No background image selected",
            wraplength=480
        )

        self.image_status.grid(
            row=1,
            column=0,
            padx=20,
            pady=(0, 10)
        )

        self.image_button_frame = ctk.CTkFrame(
            self.image_frame,
            fg_color="transparent"
        )

        self.image_button_frame.grid(
            row=2,
            column=0,
            pady=(0, 15)
        )

        self.choose_image_button = ctk.CTkButton(
            self.image_button_frame,
            text="Choose Image",
            command=self.choose_image
        )

        self.choose_image_button.grid(
            row=0,
            column=0,
            padx=5
        )

        self.remove_image_button = ctk.CTkButton(
            self.image_button_frame,
            text="Remove Image",
            command=self.remove_image
        )

        self.remove_image_button.grid(
            row=0,
            column=1,
            padx=5
        )

        # ==================================================
        # ACTION BUTTONS
        # ==================================================

        self.action_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        self.action_frame.grid(
            row=5,
            column=0,
            sticky="ew",
            pady=(18, 5)
        )

        self.action_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.action_frame.grid_columnconfigure(
            1,
            weight=1
        )

        self.apply_button = ctk.CTkButton(
            self.action_frame,
            text="Apply Theme",
            command=self.apply
        )

        self.apply_button.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 5)
        )

        self.cancel_button = ctk.CTkButton(
            self.action_frame,
            text="Cancel",
            command=self.cancel
        )

        self.cancel_button.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(5, 0)
        )

    # ==================================================
    # WINDOW VISIBILITY
    # ==================================================

    def show(self):
        self.refresh()

        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()

        self.visible = True

    def hide(self):
        self.window.withdraw()
        self.visible = False

    def cancel(self):
        """
        Discard unsaved selections and close.
        """

        self.refresh()
        self.hide()

    # ==================================================
    # REFRESH CURRENT VALUES
    # ==================================================

    def refresh(self):

        theme_manager = self.timer.theme_manager

        preset = theme_manager.get_preset()

        self.choice.set(
            preset
        )

        self.selected_background_image = (
            theme_manager.get_background_image()
        )

        self.update_image_status()

        self.preview(
            preset
        )

    # ==================================================
    # PREVIEW
    # ==================================================

    def preview(self, preset_name):

        if preset_name not in CUSTOM_PRESETS:
            preset_name = "Classic"

        colors = CUSTOM_PRESETS[
            preset_name
        ]

        background = colors["bg_start"]
        text_color = colors["text"]
        accent = colors["accent"]

        self.preview_box.configure(
            fg_color=background
        )

        self.preview_label.configure(
            text_color=text_color
        )

        self.preview_button.configure(
            fg_color=accent,
            hover_color=accent,
            text_color=text_color
        )

    # ==================================================
    # BACKGROUND IMAGE
    # ==================================================

    def choose_image(self):

        path = filedialog.askopenfilename(
            parent=self.window,
            title="Choose Background Image",
            filetypes=[
                (
                    "Image Files",
                    "*.png *.jpg *.jpeg *.webp"
                ),
                (
                    "All Files",
                    "*.*"
                ),
            ]
        )

        if not path:
            return

        self.selected_background_image = path

        self.update_image_status()

    def remove_image(self):

        self.selected_background_image = ""

        self.update_image_status()

    def update_image_status(self):

        path = self.selected_background_image

        if path:
            filename = os.path.basename(
                path
            )

            self.image_status.configure(
                text=f"Selected: {filename}"
            )

        else:
            self.image_status.configure(
                text="No background image selected"
            )

    # ==================================================
    # APPLY CUSTOM THEME
    # ==================================================

    def apply(self):
        """
        Save the selected preset and background image,
        activate Custom mode, then repaint the application.
        """

        preset = self.choice.get()

        if preset not in CUSTOM_PRESETS:
            preset = "Classic"

        # Save both preset and background image together.
        self.timer.theme_manager.set_custom(
            preset=preset,
            background_image=self.selected_background_image
        )

        # Update timer metadata
        self.timer.appearance_mode = "Custom"
        self.timer.theme = preset

        # CustomTkinter itself still needs a valid
        # Light/Dark/System mode.
        ctk.set_appearance_mode(
            self.timer.theme_manager.ctk_mode()
        )

        # Rebuild the palette from the newly selected theme.
        self.timer.palette = (
            self.timer.theme_manager.resolve(
                ctk.get_appearance_mode()
            )
        )

        # Apply the new colors to the running application.
        self.timer.apply_custom_theme()

        # Refresh settings if available.
        if (
            hasattr(
                self.timer,
                "settings_panel"
            )
            and self.timer.settings_panel is not None
        ):
            self.timer.settings_panel.refresh_theme()

        self.hide()