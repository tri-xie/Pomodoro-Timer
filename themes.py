import json, os

PRESETS = {
    "Classic": {"bg_start": "#F7F7F7", "bg_end": "#E8EEF7", "accent": "#3B82F6", "text": "#111111"},
    "Ocean": {"bg_start": "#0F4C5C", "bg_end": "#1B9AAA", "accent": "#F4D35E", "text": "#FFFFFF"},
    "Sunset": {"bg_start": "#5F0F40", "bg_end": "#E36414", "accent": "#FFB703", "text": "#FFFFFF"},
    "Forest": {"bg_start": "#143D2B", "bg_end": "#2D6A4F", "accent": "#95D5B2", "text": "#FFFFFF"},
    "Midnight": {"bg_start": "#0B1020", "bg_end": "#1F2A44", "accent": "#8B5CF6", "text": "#FFFFFF"},
    "Rose": {"bg_start": "#7B2CBF", "bg_end": "#FF758F", "accent": "#FFD6E0", "text": "#FFFFFF"},
}

class ThemeStore:
    def __init__(self, path):
        self.path = path
        self.data = {"preset": "Classic", "background_image": ""}
        self.load()

    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                self.data.update(data)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except OSError:
            pass

    def set(self, preset=None, background_image=None):
        if preset in PRESETS:
            self.data["preset"] = preset
        if background_image is not None:
            self.data["background_image"] = background_image
        self.save()

    @property
    def colors(self):
        return PRESETS.get(self.data.get("preset"), PRESETS["Classic"])
