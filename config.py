import json
import os

BASE_DIR = os.path.dirname(__file__)
ICON_PATH = os.path.join(BASE_DIR, "app logo.ico")
LOGO_PATH = os.path.join(BASE_DIR, "app logo.jpg")
SETTINGS_PATH = os.path.join(BASE_DIR, "user_settings.json")
HISTORY_PATH = os.path.join(BASE_DIR, "session_history.json")
TASKS_PATH = os.path.join(BASE_DIR, "scheduled_tasks.json")
THEME_PATH = os.path.join(BASE_DIR, "custom_theme.json")

BG_COLOR = "#2C3E50"      # Dark Slate Blue
TEXT_COLOR = "#ECF0F1"    # Off-White
WORK_COLOR = "#E74C3C"    # Tomato Red
BREAK_COLOR = "#2ECC71"   # Emerald Green
INCLUDE_PAUSE_BUTTON = True  # Set to False if users do not want the Pause/Resume option
INCLUDE_SKIP_BUTTON = False  # Set to True to enable the Skip session option by default
ENABLE_SESSION_ALERTS = True  # Play a sound and show a notification when a session ends
ALERT_VOLUME = 80  # 0-100
SHOW_NOTIFICATIONS = True
NOTIFICATION_TITLE = "Pomodoro Timer"
NOTIFICATION_MESSAGE = "{session} Session complete."
SOUND_CHOICES = ["System Default", "Information", "Warning", "Error", "Custom", "None"]
WORK_SOUND = "System Default"
SHORT_BREAK_SOUND = "Information"
LONG_BREAK_SOUND = "Warning"
WORK_CUSTOM_SOUND = ""
SHORT_BREAK_CUSTOM_SOUND = ""
LONG_BREAK_CUSTOM_SOUND = ""

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
    "enable_session_alerts": ENABLE_SESSION_ALERTS,
    "alert_volume": ALERT_VOLUME,
    "show_notifications": SHOW_NOTIFICATIONS,
    "notification_title": NOTIFICATION_TITLE,
    "notification_message": NOTIFICATION_MESSAGE,
    "work_sound": WORK_SOUND,
    "short_break_sound": SHORT_BREAK_SOUND,
    "long_break_sound": LONG_BREAK_SOUND,
    "work_custom_sound": WORK_CUSTOM_SOUND,
    "short_break_custom_sound": SHORT_BREAK_CUSTOM_SOUND,
    "long_break_custom_sound": LONG_BREAK_CUSTOM_SOUND,
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

    # Keep persisted settings from crashing the app if the JSON was edited or
    # partially corrupted. Fall back to safe defaults for invalid values.
    if merged["theme"] not in THEME_CHOICES:
        merged["theme"] = DEFAULT_THEME

    for key in ("work_min", "short_break_min", "long_break_min"):
        try:
            value = int(merged[key])
            merged[key] = value if value > 0 else DEFAULT_SETTINGS[key]
        except (TypeError, ValueError):
            merged[key] = DEFAULT_SETTINGS[key]

    for key, choices in (("app_font_family", APP_FONT_CHOICES), ("message_font_family", MESSAGE_FONT_CHOICES)):
        if merged[key] not in choices:
            merged[key] = DEFAULT_SETTINGS[key]

    for key in ("include_pause", "include_skip", "enable_session_alerts", "show_notifications"):
        if not isinstance(merged[key], bool):
            merged[key] = DEFAULT_SETTINGS[key]


    try:
        merged["alert_volume"] = max(0, min(100, int(merged["alert_volume"])))
    except (TypeError, ValueError):
        merged["alert_volume"] = ALERT_VOLUME

    for key in ("notification_title", "notification_message", "work_custom_sound", "short_break_custom_sound", "long_break_custom_sound"):
        if not isinstance(merged[key], str):
            merged[key] = DEFAULT_SETTINGS[key]

    for key in ("work_sound", "short_break_sound", "long_break_sound"):
        if merged[key] not in SOUND_CHOICES:
            merged[key] = DEFAULT_SETTINGS[key]

    for key in ("work_message", "short_break_message", "long_break_message"):
        if not isinstance(merged[key], str) or not merged[key].strip():
            merged[key] = DEFAULT_SETTINGS[key]

    return merged


def save_user_settings(settings):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except OSError:
        pass
