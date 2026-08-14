import customtkinter as ctk
from datetime import datetime


class SchedulerPanel:
    def __init__(self, parent, timer):
        self.timer = timer
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Schedule Focus Session")
        self.window.geometry("600x560")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        self.window.withdraw()
        self.visible = False

        ctk.CTkLabel(
            self.window, text="Schedule a Focus Session",
            font=("Helvetica", 22, "bold")
        ).pack(pady=(20, 12))

        form = ctk.CTkFrame(self.window)
        form.pack(fill="x", padx=25, pady=8)

        ctk.CTkLabel(form, text="Task title").pack(anchor="w", padx=18, pady=(15, 3))
        self.title_entry = ctk.CTkEntry(form, placeholder_text="e.g. Finish project proposal")
        self.title_entry.pack(fill="x", padx=18)

        ctk.CTkLabel(form, text="Date (YYYY-MM-DD)").pack(anchor="w", padx=18, pady=(12, 3))
        self.date_entry = ctk.CTkEntry(form)
        self.date_entry.pack(fill="x", padx=18)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ctk.CTkLabel(form, text="Time (HH:MM, 24-hour)").pack(anchor="w", padx=18, pady=(12, 3))
        self.time_entry = ctk.CTkEntry(form)
        self.time_entry.pack(fill="x", padx=18)
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))

        ctk.CTkLabel(form, text="Focus duration (minutes)").pack(anchor="w", padx=18, pady=(12, 3))
        self.duration = ctk.CTkEntry(form)
        self.duration.pack(fill="x", padx=18)
        self.duration.insert(0, str(timer.work_min))

        self.status = ctk.CTkLabel(form, text="")
        self.status.pack(pady=8)

        ctk.CTkButton(
            form, text="Schedule", command=self.add_task
        ).pack(pady=(3, 15))

        ctk.CTkLabel(
            self.window, text="Upcoming sessions",
            font=("Helvetica", 17, "bold")
        ).pack(anchor="w", padx=25, pady=(12, 5))

        self.listbox = ctk.CTkTextbox(self.window, height=150)
        self.listbox.pack(fill="x", padx=25)
        self.start_button = ctk.CTkButton(
            self.window, text="Start Selected", command=self.start_selected
        )
        self.start_button.pack(pady=10)
        self.selected_id = None

        self.listbox.bind("<Button-1>", self.select_by_click)

    def show(self):
        self.refresh()
        self.window.deiconify()
        self.window.lift()
        self.visible = True

    def hide(self):
        self.window.withdraw()
        self.visible = False

    def add_task(self):
        title = self.title_entry.get().strip()
        try:
            scheduled = datetime.strptime(
                f"{self.date_entry.get().strip()} {self.time_entry.get().strip()}",
                "%Y-%m-%d %H:%M"
            )
            duration = int(self.duration.get())
            if duration <= 0:
                raise ValueError
            if not title:
                raise ValueError
        except ValueError:
            self.status.configure(text="Enter a title, valid date/time, and positive duration.")
            return
        self.timer.task_store.add(title, scheduled.isoformat(timespec="minutes"), duration)
        self.status.configure(text="Session scheduled.")
        self.title_entry.delete(0, "end")
        self.refresh()

    def refresh(self):
        self.listbox.configure(state="normal")
        self.listbox.delete("1.0", "end")
        for item in self.timer.task_store.upcoming():
            self.listbox.insert(
                "end",
                f"{item['scheduled_for'].replace('T',' ')} | "
                f"{item['title']} | {item['duration_minutes']} min\n"
            )
        self.listbox.configure(state="disabled")

    def select_by_click(self, _event):
        # Selection is intentionally simple: the first upcoming item is selected
        # when the user clicks the list. Start Selected remains deterministic.
        items = self.timer.task_store.upcoming()
        self.selected_id = items[0]["id"] if items else None

    def start_selected(self):
        items = self.timer.task_store.upcoming()
        task = next((t for t in items if t["id"] == self.selected_id), None)
        if task:
            self.timer.start_scheduled_task(task)
            self.hide()
