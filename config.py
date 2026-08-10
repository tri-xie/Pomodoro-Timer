import json
import os

BASE_DIR = os.path.dirname(__file__)
ICON_PATH = os.path.join(BASE_DIR, "app logo.ico")
LOGO_PATH = os.path.join(BASE_DIR, "app logo.jpg")
SETTINGS_PATH = os.path.join(BASE_DIR, "user_settings.json")

BG_COLOR = "#2C3E50"      # Dark Slate Blue
TEXT_COLOR = "#ECF0F1"    # Off-White
WORK_COLOR = "#E74C3C"    # Tomato Red
BREAK_COLOR = "#2ECC71"   # Emerald Green
INCLUDE_PAUSE_BUTTON = True  # Set to False if users do not want the Pause/Resume option
INCLUDE_SKIP_BUTTON = False  # Set to True to enable the Skip session option by default

WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20

APP_FONT_FAMILY = "Courier"
MESSAGE_FONT_FAMILY = "Helvetica"
APP_FONT_CHOICES = ["Courier", "Helvetica", "Times", "Arial", "Consolas"]
MESSAGE_FONT_CHOICES = ["Courier", "Helvetica", "Times", "Arial", "Consolas"]

WORK_MESSAGE = "Focus on your task!"
SHORT_BREAK_MESSAGE = "Take a short, refreshing break."
LONG_BREAK_MESSAGE = "Enjoy your longer break and recharge."

DEFAULT_THEME = "Light"
THEME_CHOICES = ["Light", "Dark"]
THEME_PALETTES = {
    "Light": {
        "APP_BG": "#f7f5dd",
        "FRAME_BG": "#ecf0f1",
        "CANVAS_BG": "#f7f5dd",
        "TEXT_COLOR": "#2c3e50",
        "BUTTON_BG": "#ecf0f1",
    },
    "Dark": {
        "APP_BG": "#1f2937",
        "FRAME_BG": "#2d3748",
        "CANVAS_BG": "#1f2937",
        "TEXT_COLOR": "#ecf0f1",
        "BUTTON_BG": "#4a5568",
    },
}

DEFAULT_SETTINGS = {
    "theme": DEFAULT_THEME,
    "work_min": WORK_MIN,
    "short_break_min": SHORT_BREAK_MIN,
    "long_break_min": LONG_BREAK_MIN,
    "work_message": WORK_MESSAGE,
    "short_break_message": SHORT_BREAK_MESSAGE,
    "long_break_message": LONG_BREAK_MESSAGE,
    "app_font_family": APP_FONT_FAMILY,
    "message_font_family": MESSAGE_FONT_FAMILY,
    "include_pause": INCLUDE_PAUSE_BUTTON,
    "include_skip": INCLUDE_SKIP_BUTTON,
}


def load_user_settings():
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            saved = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_SETTINGS.copy()

    merged = DEFAULT_SETTINGS.copy()
    if isinstance(saved, dict):
        merged.update({k: saved[k] for k in merged.keys() if k in saved})
    return merged


def save_user_settings(settings):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except OSError:
        pass
