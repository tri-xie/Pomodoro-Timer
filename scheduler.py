import customtkinter as ctk
from datetime import datetime


class SchedulerPanel:

    def __init__(
        self,
        parent,
        timer
    ):

        self.parent = parent
        self.timer = timer

        self.visible = False
        self.selected_id = None

        # ==================================================
        # CREATE WINDOW
        # ==================================================

        self.window = ctk.CTkToplevel(
            parent
        )

        # Immediately hide the window while its widgets
        # are being created. This prevents startup flashing.
        self.window.withdraw()

        self.window.title(
            "Schedule Focus Session"
        )

        self.window.geometry(
            "600x560"
        )

        self.window.minsize(
            600,
            560
        )

        self.window.resizable(
            False,
            False
        )

        self.window.protocol(
            "WM_DELETE_WINDOW",
            self.hide
        )

        # ==================================================
        # TITLE
        # ==================================================

        ctk.CTkLabel(
            self.window,
            text="Schedule a Focus Session",
            font=(
                "Helvetica",
                22,
                "bold"
            )
        ).pack(
            pady=(20, 12)
        )

        # ==================================================
        # FORM
        # ==================================================

        form = ctk.CTkFrame(
            self.window
        )

        form.pack(
            fill="x",
            padx=25,
            pady=8
        )

        # --------------------------------------------------
        # TASK TITLE
        # --------------------------------------------------

        ctk.CTkLabel(
            form,
            text="Task title"
        ).pack(
            anchor="w",
            padx=18,
            pady=(15, 3)
        )

        self.title_entry = ctk.CTkEntry(
            form,
            placeholder_text=(
                "e.g. Finish project proposal"
            )
        )

        self.title_entry.pack(
            fill="x",
            padx=18
        )

        # --------------------------------------------------
        # DATE
        # --------------------------------------------------

        ctk.CTkLabel(
            form,
            text="Date (YYYY-MM-DD)"
        ).pack(
            anchor="w",
            padx=18,
            pady=(12, 3)
        )

        self.date_entry = ctk.CTkEntry(
            form
        )

        self.date_entry.pack(
            fill="x",
            padx=18
        )

        self.date_entry.insert(
            0,
            datetime.now().strftime(
                "%Y-%m-%d"
            )
        )

        # --------------------------------------------------
        # TIME
        # --------------------------------------------------

        ctk.CTkLabel(
            form,
            text="Time (HH:MM, 24-hour)"
        ).pack(
            anchor="w",
            padx=18,
            pady=(12, 3)
        )

        self.time_entry = ctk.CTkEntry(
            form
        )

        self.time_entry.pack(
            fill="x",
            padx=18
        )

        self.time_entry.insert(
            0,
            datetime.now().strftime(
                "%H:%M"
            )
        )

        # --------------------------------------------------
        # DURATION
        # --------------------------------------------------

        ctk.CTkLabel(
            form,
            text="Focus duration (minutes)"
        ).pack(
            anchor="w",
            padx=18,
            pady=(12, 3)
        )

        self.duration = ctk.CTkEntry(
            form
        )

        self.duration.pack(
            fill="x",
            padx=18
        )

        self.duration.insert(
            0,
            str(
                timer.work_min
            )
        )

        # --------------------------------------------------
        # STATUS
        # --------------------------------------------------

        self.status = ctk.CTkLabel(
            form,
            text=""
        )

        self.status.pack(
            pady=8
        )

        # --------------------------------------------------
        # SCHEDULE BUTTON
        # --------------------------------------------------

        ctk.CTkButton(
            form,
            text="Schedule",
            command=self.add_task
        ).pack(
            pady=(3, 15)
        )

        # ==================================================
        # UPCOMING SESSIONS
        # ==================================================

        ctk.CTkLabel(
            self.window,
            text="Upcoming sessions",
            font=(
                "Helvetica",
                17,
                "bold"
            )
        ).pack(
            anchor="w",
            padx=25,
            pady=(12, 5)
        )

        self.listbox = ctk.CTkTextbox(
            self.window,
            height=150
        )

        self.listbox.pack(
            fill="x",
            padx=25
        )

        # ==================================================
        # START SELECTED BUTTON
        # ==================================================

        self.start_button = ctk.CTkButton(
            self.window,
            text="Start Selected",
            command=self.start_selected
        )

        self.start_button.pack(
            pady=10
        )

        # ==================================================
        # SELECTION
        # ==================================================

        self.listbox.bind(
            "<Button-1>",
            self.select_by_click
        )

        # ==================================================
        # FINALIZE WINDOW WHILE HIDDEN
        # ==================================================

        self.window.update_idletasks()

        self.window.withdraw()


    # ======================================================
    # SHOW
    # ======================================================

    def show(self):

        self.refresh()

        # Make sure the window geometry is fully calculated
        # before it becomes visible.
        self.window.update_idletasks()

        self.window.deiconify()

        self.window.lift()

        self.window.focus_force()

        self.visible = True


    # ======================================================
    # HIDE
    # ======================================================

    def hide(self):

        try:

            self.window.withdraw()

        except Exception:

            pass

        self.visible = False


    # ======================================================
    # ADD TASK
    # ======================================================

    def add_task(self):

        title = (
            self.title_entry.get()
            .strip()
        )

        try:

            scheduled = datetime.strptime(

                f"{self.date_entry.get().strip()} "
                f"{self.time_entry.get().strip()}",

                "%Y-%m-%d %H:%M"
            )

            duration = int(
                self.duration.get()
            )

            if duration <= 0:

                raise ValueError

            if not title:

                raise ValueError

        except ValueError:

            self.status.configure(
                text=(
                    "Enter a title, valid date/time, "
                    "and positive duration."
                )
            )

            return

        self.timer.task_store.add(

            title,

            scheduled.isoformat(
                timespec="minutes"
            ),

            duration
        )

        self.status.configure(
            text="Session scheduled."
        )

        self.title_entry.delete(
            0,
            "end"
        )

        self.refresh()


    # ======================================================
    # REFRESH TASK LIST
    # ======================================================

    def refresh(self):

        self.listbox.configure(
            state="normal"
        )

        self.listbox.delete(
            "1.0",
            "end"
        )

        items = (
            self.timer.task_store.upcoming()
        )

        for item in items:

            self.listbox.insert(

                "end",

                f"{item['scheduled_for'].replace('T', ' ')} | "
                f"{item['title']} | "
                f"{item['duration_minutes']} min\n"
            )

        self.listbox.configure(
            state="disabled"
        )

        # Clear the selected task if it no longer exists.
        if self.selected_id is not None:

            task_exists = any(

                item["id"] == self.selected_id

                for item in items
            )

            if not task_exists:

                self.selected_id = None


    # ======================================================
    # SELECT TASK
    # ======================================================

    def select_by_click(
        self,
        _event
    ):

        # The current scheduler implementation keeps
        # selection simple and deterministic.
        items = (
            self.timer.task_store.upcoming()
        )

        self.selected_id = (

            items[0]["id"]

            if items

            else None
        )


    # ======================================================
    # START SELECTED TASK
    # ======================================================

    def start_selected(self):

        items = (
            self.timer.task_store.upcoming()
        )

        task = next(

            (

                task

                for task in items

                if task["id"] == self.selected_id

            ),

            None
        )

        if task:

            self.timer.start_scheduled_task(
                task
            )

            self.hide()