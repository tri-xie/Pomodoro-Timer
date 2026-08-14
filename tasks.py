import json
import uuid
from datetime import datetime


class TaskStore:
    def __init__(self, path):
        self.path = path
        self.tasks = []
        self.load()

    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.tasks = data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            self.tasks = []

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, indent=2)
        except OSError:
            pass

    def add(self, title, scheduled_for, duration_minutes):
        item = {
            "id": str(uuid.uuid4()),
            "title": title.strip(),
            "scheduled_for": scheduled_for,
            "duration_minutes": int(duration_minutes),
            "completed": False,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        self.tasks.append(item)
        self.save()
        return item

    def update(self, task_id, **changes):
        for item in self.tasks:
            if item.get("id") == task_id:
                item.update(changes)
                self.save()
                return item
        return None

    def delete(self, task_id):
        self.tasks = [t for t in self.tasks if t.get("id") != task_id]
        self.save()

    def upcoming(self):
        return sorted(
            [t for t in self.tasks if not t.get("completed")],
            key=lambda t: t.get("scheduled_for", "")
        )
