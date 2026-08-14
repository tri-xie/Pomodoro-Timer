import os
import json
from datetime import datetime


class SessionHistory:
    def __init__(self, path):
        self.path = path
        self.sessions = []
        self.load()

    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.sessions = data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            self.sessions = []

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.sessions, f, indent=2)
        except OSError:
            pass

    def add_session(self, session_type, duration_minutes, completed=True):
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "type": session_type,
            "duration_minutes": int(duration_minutes),
            "completed": bool(completed),
        }
        self.sessions.append(entry)
        self.save()

    def clear(self):
        self.sessions = []
        self.save()

    def summary(self):
        completed = [s for s in self.sessions if s.get("completed")]
        work = [s for s in completed if s.get("type") == "Work"]
        short = [s for s in completed if s.get("type") == "Short Break"]
        long = [s for s in completed if s.get("type") == "Long Break"]
        return {
            "total": len(completed),
            "work": len(work),
            "short_breaks": len(short),
            "long_breaks": len(long),
            "focus_minutes": sum(s.get("duration_minutes", 0) for s in work),
        }


    def daily_stats(self, days=7):
        from datetime import datetime, timedelta
        today = datetime.now().date()
        result = []
        for offset in range(days - 1, -1, -1):
            day = today - timedelta(days=offset)
            key = day.isoformat()
            sessions = [
                s for s in self.sessions
                if s.get("completed") and str(s.get("timestamp", "")).startswith(key)
            ]
            work = [s for s in sessions if s.get("type") == "Work"]
            result.append({
                "date": day,
                "label": day.strftime("%a"),
                "sessions": len(work),
                "focus_minutes": sum(int(s.get("duration_minutes", 0)) for s in work),
            })
        return result

    def weekly_stats(self, weeks=8):
        from datetime import datetime, timedelta
        today = datetime.now().date()
        current_monday = today - timedelta(days=today.weekday())
        result = []
        for offset in range(weeks - 1, -1, -1):
            monday = current_monday - timedelta(weeks=offset)
            sunday = monday + timedelta(days=6)
            sessions = []
            for item in self.sessions:
                if not item.get("completed") or item.get("type") != "Work":
                    continue
                try:
                    day = datetime.fromisoformat(item.get("timestamp", "")).date()
                except (ValueError, TypeError):
                    continue
                if monday <= day <= sunday:
                    sessions.append(item)
            result.append({
                "start": monday,
                "end": sunday,
                "label": monday.strftime("%b %-d") if os.name != "nt" else monday.strftime("%b %#d"),
                "sessions": len(sessions),
                "focus_minutes": sum(int(s.get("duration_minutes", 0)) for s in sessions),
            })
        return result


    def analytics(self, daily_goal=4):
        from datetime import datetime, timedelta
        completed = [s for s in self.sessions if s.get("completed")]
        work = [s for s in completed if s.get("type") == "Work"]

        by_day = {}
        for item in work:
            try:
                day = datetime.fromisoformat(item.get("timestamp", "")).date()
            except (ValueError, TypeError):
                continue
            by_day[day.isoformat()] = by_day.get(day.isoformat(), 0) + 1

        today = datetime.now().date()
        streak = 0
        cursor = today
        while by_day.get(cursor.isoformat(), 0) > 0:
            streak += 1
            cursor -= timedelta(days=1)

        best_day = None
        if by_day:
            best_key = max(by_day, key=by_day.get)
            best_day = {"date": best_key, "sessions": by_day[best_key]}

        total_work = len(work)
        completed_all = len(completed)
        completion_rate = (total_work / completed_all * 100) if completed_all else 0

        return {
            "streak_days": streak,
            "best_day": best_day,
            "completion_rate": completion_rate,
            "today_sessions": by_day.get(today.isoformat(), 0),
            "daily_goal": int(daily_goal),
            "by_day": by_day,
        }
