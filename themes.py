import json
import os


# ==========================================================
# STANDARD LIGHT THEME
# ==========================================================

LIGHT_PALETTE = {
    "APP_BG": "#F7F5DD",
    "FRAME_BG": "#ECF0F1",
    "CANVAS_BG": "#F7F5DD",
    "TEXT_COLOR": "#2C3E50",
    "BUTTON_BG": "#DCE3E6",
}


# ==========================================================
# STANDARD DARK THEME
# ==========================================================

DARK_PALETTE = {
    "APP_BG": "#1F2937",
    "FRAME_BG": "#2D3748",
    "CANVAS_BG": "#1F2937",
    "TEXT_COLOR": "#ECF0F1",
    "BUTTON_BG": "#4A5568",
}


# ==========================================================
# CUSTOM THEME PRESETS
#
# Used by theme_customizer.py
# ==========================================================

CUSTOM_PRESETS = {
    "Classic": {
        "bg_start": "#F7F7F7",
        "bg_end": "#E8EEF7",
        "accent": "#3B82F6",
        "text": "#111111",
    },

    "Ocean": {
        "bg_start": "#0F4C5C",
        "bg_end": "#1B9AAA",
        "accent": "#F4D35E",
        "text": "#FFFFFF",
    },

    "Sunset": {
        "bg_start": "#5F0F40",
        "bg_end": "#E36414",
        "accent": "#FFB703",
        "text": "#FFFFFF",
    },

    "Forest": {
        "bg_start": "#143D2B",
        "bg_end": "#2D6A4F",
        "accent": "#95D5B2",
        "text": "#FFFFFF",
    },

    "Midnight": {
        "bg_start": "#0B1020",
        "bg_end": "#1F2A44",
        "accent": "#8B5CF6",
        "text": "#FFFFFF",
    },

    "Rose": {
        "bg_start": "#7B2CBF",
        "bg_end": "#FF758F",
        "accent": "#FFD6E0",
        "text": "#FFFFFF",
    },
}


# ==========================================================
# BACKWARD COMPATIBILITY
#
# Some older versions of the project may import PRESETS.
# ==========================================================

PRESETS = CUSTOM_PRESETS


# ==========================================================
# VALID MODES
# ==========================================================

VALID_MODES = (
    "Light",
    "Dark",
    "System",
    "Custom",
)


# ==========================================================
# THEME MANAGER
# ==========================================================

class ThemeManager:
    """
    Single source of truth for all application themes.

    Supported modes:

        Light
        Dark
        System
        Custom

    Custom mode uses one of the presets in CUSTOM_PRESETS
    and may optionally have a background image.
    """

    def __init__(self, path):
        self.path = path

        self.data = {
            "mode": "Light",
            "preset": "Classic",
            "background_image": "",
        }

        self.load()

    # ------------------------------------------------------
    # LOAD
    # ------------------------------------------------------

    def load(self):
        """
        Load saved theme settings.

        Invalid or missing data falls back safely to
        the default Light / Classic configuration.
        """

        try:
            if os.path.isfile(self.path):
                with open(
                    self.path,
                    "r",
                    encoding="utf-8"
                ) as file:
                    saved = json.load(file)

                if isinstance(saved, dict):
                    self.data.update(saved)

        except (
            FileNotFoundError,
            json.JSONDecodeError,
            OSError,
        ):
            pass

        # Validate mode
        if self.data.get("mode") not in VALID_MODES:
            self.data["mode"] = "Light"

        # Validate preset
        if self.data.get("preset") not in CUSTOM_PRESETS:
            self.data["preset"] = "Classic"

        # Validate background image value
        background_image = self.data.get(
            "background_image",
            ""
        )

        if not isinstance(
            background_image,
            str
        ):
            self.data["background_image"] = ""

    # ------------------------------------------------------
    # SAVE
    # ------------------------------------------------------

    def save(self):
        """
        Save theme settings to disk.
        """

        try:
            directory = os.path.dirname(
                self.path
            )

            if directory:
                os.makedirs(
                    directory,
                    exist_ok=True
                )

            with open(
                self.path,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    self.data,
                    file,
                    indent=4
                )

        except OSError:
            pass

    # ------------------------------------------------------
    # MODE
    # ------------------------------------------------------

    def set_mode(self, mode):
        """
        Set one of the supported appearance modes.
        """

        if mode not in VALID_MODES:
            raise ValueError(
                f"Unsupported theme mode: {mode}"
            )

        self.data["mode"] = mode

        self.save()

    def get_mode(self):
        """
        Return the currently selected theme mode.
        """

        return self.data.get(
            "mode",
            "Light"
        )

    # ------------------------------------------------------
    # CUSTOM THEME
    # ------------------------------------------------------

    def set_custom(
        self,
        preset=None,
        background_image=None
    ):
        """
        Activate Custom mode.

        Optionally changes the preset and/or
        background image.
        """

        if (
            preset is not None
            and preset not in CUSTOM_PRESETS
        ):
            raise ValueError(
                f"Unsupported custom preset: {preset}"
            )

        if preset is not None:
            self.data["preset"] = preset

        if background_image is not None:
            self.data[
                "background_image"
            ] = background_image

        self.data["mode"] = "Custom"

        self.save()

    # ------------------------------------------------------
    # BACKWARD COMPATIBILITY
    # ------------------------------------------------------

    def set(
        self,
        preset=None,
        background_image=None
    ):
        """
        Backward-compatible method.

        Older versions of theme_customizer.py may call:

            theme_manager.set(...)
        """

        self.set_custom(
            preset=preset,
            background_image=background_image
        )

    # ------------------------------------------------------
    # PRESET
    # ------------------------------------------------------

    def set_preset(self, preset):
        """
        Change the custom preset.

        This automatically activates Custom mode.
        """

        self.set_custom(
            preset=preset
        )

    def get_preset(self):
        """
        Return the currently selected preset.
        """

        preset = self.data.get(
            "preset",
            "Classic"
        )

        if preset not in CUSTOM_PRESETS:
            preset = "Classic"

        return preset

    # ------------------------------------------------------
    # BACKGROUND IMAGE
    # ------------------------------------------------------

    def set_background_image(self, path):
        """
        Set a custom background image.

        Passing an empty string removes it.
        """

        if path is None:
            path = ""

        self.data["background_image"] = path

        self.save()

    def get_background_image(self):
        """
        Return the saved background image path.
        """

        return self.data.get(
            "background_image",
            ""
        )

    def clear_background_image(self):
        """
        Remove the current background image.
        """

        self.data["background_image"] = ""

        self.save()

    # ------------------------------------------------------
    # COLORS
    # ------------------------------------------------------

    @property
    def colors(self):
        """
        Return the active custom preset colors.
        """

        preset = self.get_preset()

        return CUSTOM_PRESETS.get(
            preset,
            CUSTOM_PRESETS["Classic"]
        )

    # ------------------------------------------------------
    # CUSTOMTKINTER MODE
    # ------------------------------------------------------

    def ctk_mode(self):
        """
        Return a mode accepted by CustomTkinter.

        CustomTkinter only understands:

            Light
            Dark
            System

        Custom is handled by our own palette resolver,
        so it falls back to System here.
        """

        mode = self.get_mode()

        if mode in (
            "Light",
            "Dark",
            "System",
        ):
            return mode

        return "System"

    # ------------------------------------------------------
    # PALETTE RESOLUTION
    # ------------------------------------------------------

    def resolve(
        self,
        detected_system_mode="Light"
    ):
        """
        Return one normalized palette.

        The result always contains:

            APP_BG
            FRAME_BG
            CANVAS_BG
            TEXT_COLOR
            BUTTON_BG
            MODE
            PRESET
            IS_CUSTOM
        """

        selected_mode = self.get_mode()

        # --------------------------------------------------
        # SYSTEM MODE
        #
        # The application needs a concrete palette for
        # normal Tkinter widgets such as Canvas.
        # --------------------------------------------------

        resolved_mode = selected_mode

        if selected_mode == "System":

            if detected_system_mode == "Dark":
                resolved_mode = "Dark"

            else:
                resolved_mode = "Light"

        # --------------------------------------------------
        # LIGHT
        # --------------------------------------------------

        if resolved_mode == "Light":

            palette = dict(
                LIGHT_PALETTE
            )

            is_custom = False

        # --------------------------------------------------
        # DARK
        # --------------------------------------------------

        elif resolved_mode == "Dark":

            palette = dict(
                DARK_PALETTE
            )

            is_custom = False

        # --------------------------------------------------
        # CUSTOM
        # --------------------------------------------------

        else:

            colors = self.colors

            palette = {
                "APP_BG":
                    colors["bg_start"],

                "FRAME_BG":
                    colors["bg_end"],

                "CANVAS_BG":
                    colors["bg_start"],

                "TEXT_COLOR":
                    colors["text"],

                "BUTTON_BG":
                    colors["accent"],
            }

            is_custom = True

        # --------------------------------------------------
        # METADATA
        # --------------------------------------------------

        palette["MODE"] = selected_mode

        palette["RESOLVED_MODE"] = (
            resolved_mode
        )

        palette["PRESET"] = (
            self.get_preset()
        )

        palette["IS_CUSTOM"] = (
            is_custom
        )

        palette["BACKGROUND_IMAGE"] = (
            self.get_background_image()
        )

        return palette


# ==========================================================
# BACKWARD COMPATIBILITY
#
# Older project files may still import ThemeStore.
# ==========================================================

ThemeStore = ThemeManager