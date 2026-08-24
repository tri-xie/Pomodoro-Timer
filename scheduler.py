import customtkinter as ctk
from datetime import datetime


class SchedulerPanel:

    DAYS = [
        ("Monday", 0),
        ("Tuesday", 1),
        ("Wednesday", 2),
        ("Thursday", 3),
        ("Friday", 4),
        ("Saturday", 5),
        ("Sunday", 6),
    ]

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

        self.window.withdraw()

        self.window.title(
            "Schedule Focus Session"
        )

        self.window.geometry(
            "680x720"
        )

        self.window.minsize(
            680,
            720
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
            pady=(18, 10)
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
            pady=5
        )

        # ==================================================
        # TITLE
        # ==================================================

        ctk.CTkLabel(
            form,
            text="Task title"
        ).pack(
            anchor="w",
            padx=18,
            pady=(12, 3)
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

        # ==================================================
        # SCHEDULE TYPE
        # ==================================================

        ctk.CTkLabel(
            form,
            text="Schedule type"
        ).pack(
            anchor="w",
            padx=18,
            pady=(10, 3)
        )

        self.schedule_type = ctk.CTkSegmentedButton(
            form,
            values=[
                "One time",
                "Recurring"
            ],
            command=self._schedule_type_changed
        )

        self.schedule_type.set(
            "One time"
        )

        self.schedule_type.pack(
            fill="x",
            padx=18
        )

        # ==================================================
        # DATE
        # ==================================================

        self.date_label = ctk.CTkLabel(
            form,
            text="Date (YYYY-MM-DD)"
        )

        self.date_label.pack(
            anchor="w",
            padx=18,
            pady=(10, 3)
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

        # ==================================================
        # TIME
        # ==================================================

        ctk.CTkLabel(
            form,
            text="Time (HH:MM, 24-hour)"
        ).pack(
            anchor="w",
            padx=18,
            pady=(10, 3)
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

        # ==================================================
        # RECURRING DAYS
        # ==================================================

        self.days_label = ctk.CTkLabel(
            form,
            text="Repeat on"
        )

        self.days_label.pack(
            anchor="w",
            padx=18,
            pady=(10, 3)
        )

        self.days_frame = ctk.CTkFrame(
            form,
            fg_color="transparent"
        )

        self.days_frame.pack(
            fill="x",
            padx=14
        )

        self.day_vars = {}

        for index, (
            day_name,
            day_number
        ) in enumerate(
            self.DAYS
        ):

            variable = ctk.BooleanVar(
                value=False
            )

            self.day_vars[
                day_number
            ] = variable

            button = ctk.CTkCheckBox(
                self.days_frame,
                text=day_name[:3],
                variable=variable
            )

            button.grid(
                row=0,
                column=index,
                padx=3,
                pady=3,
                sticky="ew"
            )

            self.days_frame.grid_columnconfigure(
                index,
                weight=1
            )

        # ==================================================
        # DURATION
        # ==================================================

        ctk.CTkLabel(
            form,
            text="Focus duration (minutes)"
        ).pack(
            anchor="w",
            padx=18,
            pady=(10, 3)
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

        # ==================================================
        # STATUS
        # ==================================================

        self.status = ctk.CTkLabel(
            form,
            text=""
        )

        self.status.pack(
            pady=7
        )

        # ==================================================
        # SCHEDULE BUTTON
        # ==================================================

        ctk.CTkButton(
            form,
            text="Schedule",
            command=self.add_task
        ).pack(
            pady=(0, 12)
        )

        # ==================================================
        # SCHEDULE LIST
        # ==================================================

        ctk.CTkLabel(
            self.window,
            text="Scheduled sessions",
            font=(
                "Helvetica",
                17,
                "bold"
            )
        ).pack(
            anchor="w",
            padx=25,
            pady=(10, 5)
        )

        self.listbox = ctk.CTkTextbox(
            self.window,
            height=180
        )

        self.listbox.pack(
            fill="x",
            padx=25
        )

        self.listbox.bind(
            "<Button-1>",
            self.select_by_click
        )

        # ==================================================
        # ACTIONS
        # ==================================================

        actions = ctk.CTkFrame(
            self.window,
            fg_color="transparent"
        )

        actions.pack(
            fill="x",
            padx=25,
            pady=10
        )

        self.start_button = ctk.CTkButton(
            actions,
            text="Start Selected",
            command=self.start_selected
        )

        self.start_button.pack(
            side="left",
            expand=True,
            padx=4
        )

        self.toggle_button = ctk.CTkButton(
            actions,
            text="Deactivate",
            command=self.toggle_selected
        )

        self.toggle_button.pack(
            side="left",
            expand=True,
            padx=4
        )

        self.delete_button = ctk.CTkButton(
            actions,
            text="Delete",
            command=self.delete_selected
        )

        self.delete_button.pack(
            side="left",
            expand=True,
            padx=4
        )

        # ==================================================
        # FINALIZE
        # ==================================================

        self._schedule_type_changed(
            "One time"
        )

        self.window.update_idletasks()

        self.window.withdraw()

    # ======================================================
    # SHOW
    # ======================================================

    def show(self):

        self.refresh()

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
    # SCHEDULE TYPE
    # ======================================================

    def _schedule_type_changed(
        self,
        value
    ):

        recurring = (
            value == "Recurring"
        )

        if recurring:

            self.date_label.pack_forget()
            self.date_entry.pack_forget()

            self.days_label.pack(
                anchor="w",
                padx=18,
                pady=(10, 3)
            )

            self.days_frame.pack(
                fill="x",
                padx=14
            )

        else:

            self.days_label.pack_forget()
            self.days_frame.pack_forget()

            self.date_label.pack(
                anchor="w",
                padx=18,
                pady=(10, 3)
            )

            self.date_entry.pack(
                fill="x",
                padx=18
            )

    # ======================================================
    # ADD TASK
    # ======================================================

    def add_task(self):

        title = (
            self.title_entry.get()
            .strip()
        )

        time_text = (
            self.time_entry.get()
            .strip()
        )

        schedule_type = (
            "recurring"
            if self.schedule_type.get()
            == "Recurring"
            else "once"
        )

        try:

            duration = int(
                self.duration.get()
            )

            if duration <= 0:

                raise ValueError

            if not title:

                raise ValueError

            datetime.strptime(
                time_text,
                "%H:%M"
            )

        except ValueError:

            self.status.configure(
                text=(
                    "Enter a title, valid time, "
                    "and positive duration."
                )
            )

            return

        # ==================================================
        # ONE-TIME
        # ==================================================

        if schedule_type == "once":

            try:

                scheduled = datetime.strptime(
                    (
                        f"{self.date_entry.get().strip()} "
                        f"{time_text}"
                    ),
                    "%Y-%m-%d %H:%M"
                )

            except ValueError:

                self.status.configure(
                    text="Enter a valid date."
                )

                return

            if scheduled <= datetime.now():

                self.status.configure(
                    text=(
                        "The scheduled time must "
                        "be in the future."
                    )
                )

                return

            self.timer.task_store.add(
                title,
                scheduled.isoformat(
                    timespec="minutes"
                ),
                duration,
                schedule_type="once"
            )

        # ==================================================
        # RECURRING
        # ==================================================

        else:

            selected_days = [

                day_number

                for day_number, variable
                in self.day_vars.items()

                if variable.get()
            ]

            if not selected_days:

                self.status.configure(
                    text=(
                        "Select at least one "
                        "day of the week."
                    )
                )

                return

            # Use today's date as the anchor date.
            # The recurring scheduler uses only the time
            # and selected weekdays.
            anchor = datetime.combine(
                datetime.now().date(),
                datetime.strptime(
                    time_text,
                    "%H:%M"
                ).time()
            )

            self.timer.task_store.add(
                title,
                anchor.isoformat(
                    timespec="minutes"
                ),
                duration,
                schedule_type="recurring",
                days=selected_days
            )

        # ==================================================
        # SUCCESS
        # ==================================================

        self.status.configure(
            text="Session scheduled."
        )

        self.title_entry.delete(
            0,
            "end"
        )

        self.refresh()

    # ======================================================
    # REFRESH
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
            self.timer.task_store.all_schedules()
        )

        for index, item in enumerate(
            items
        ):

            schedule_type = item.get(
                "schedule_type",
                "once"
            )

            active = item.get(
                "active",
                True
            )

            if schedule_type == "once":

                scheduled = item.get(
                    "scheduled_for",
                    ""
                ).replace(
                    "T",
                    " "
                )

                repeat_text = "Once"

            else:

                occurrence = (
                    self.timer.task_store
                    .display_datetime(item)
                )

                scheduled = (
                    occurrence.strftime(
                        "%Y-%m-%d %H:%M"
                    )
                    if occurrence
                    else "No upcoming occurrence"
                )

                day_names = [

                    self.DAYS[day][0][:3]

                    for day in item.get(
                        "days",
                        []
                    )

                    if 0 <= day < 7
                ]

                repeat_text = (
                    ", ".join(day_names)
                    if day_names
                    else "Recurring"
                )

            if (
                item.get(
                    "notified",
                    False
                )
                and schedule_type == "once"
            ):

                status = "READY"

            elif active:

                status = "ACTIVE"

            else:

                status = "INACTIVE"

            self.listbox.insert(
                "end",
                (
                    f"{index + 1}. "
                    f"{scheduled} | "
                    f"{item.get('title', '')} | "
                    f"{item.get('duration_minutes', 0)} min | "
                    f"{repeat_text} | "
                    f"{status}\n"
                )
            )

        self.listbox.configure(
            state="disabled"
        )

        # ==================================================
        # SELECTED TASK
        # ==================================================

        if self.selected_id is not None:

            task = self.timer.task_store.get(
                self.selected_id
            )

            if task is None:

                self.selected_id = None

        self._update_action_buttons()

    # ======================================================
    # SELECT BY CLICK
    # ======================================================

    def select_by_click(
        self,
        event
    ):

        # Determine which textbox line was clicked.
        try:

            index = int(
                self.listbox.index(
                    f"@{event.x},{event.y}"
                ).split(".")[0]
            ) - 1

        except Exception:

            return

        items = (
            self.timer.task_store.all_schedules()
        )

        if (
            index < 0
            or index >= len(items)
        ):

            self.selected_id = None

        else:

            self.selected_id = (
                items[index]["id"]
            )

        self._update_action_buttons()

    # ======================================================
    # UPDATE ACTION BUTTONS
    # ======================================================

    def _update_action_buttons(self):

        task = None

        if self.selected_id is not None:

            task = self.timer.task_store.get(
                self.selected_id
            )

        if task is None:

            self.start_button.configure(
                state="disabled"
            )

            self.toggle_button.configure(
                state="disabled"
            )

            self.delete_button.configure(
                state="disabled"
            )

            return

        self.start_button.configure(
            state="normal"
        )

        self.delete_button.configure(
            state="normal"
        )

        if task.get(
            "schedule_type",
            "once"
        ) == "recurring":

            self.toggle_button.configure(
                state="normal",
                text=(
                    "Deactivate"
                    if task.get(
                        "active",
                        True
                    )
                    else "Activate"
                )
            )

        else:

            self.toggle_button.configure(
                state="disabled",
                text="Deactivate"
            )

    # ======================================================
    # START SELECTED
    # ======================================================

    def start_selected(self):

        if self.selected_id is None:

            return

        task = self.timer.task_store.get(
            self.selected_id
        )

        if task is None:

            return

        self.timer.start_scheduled_task(
            task
        )

        # One-time schedules are completed when the
        # user actually chooses to start them.
        if task.get(
            "schedule_type",
            "once"
        ) == "once":

            self.timer.task_store.complete_one_time(
                task["id"]
            )

        self.hide()

    # ======================================================
    # ACTIVATE / DEACTIVATE
    # ======================================================

    def toggle_selected(self):

        if self.selected_id is None:

            return

        task = self.timer.task_store.get(
            self.selected_id
        )

        if task is None:

            return

        if task.get(
            "schedule_type",
            "once"
        ) != "recurring":

            return

        current = task.get(
            "active",
            True
        )

        self.timer.task_store.set_active(
            task["id"],
            not current
        )

        self.refresh()

    # ======================================================
    # DELETE
    # ======================================================

    def delete_selected(self):

        if self.selected_id is None:

            return

        task = self.timer.task_store.get(
            self.selected_id
        )

        if task is None:

            return

        self.timer.task_store.delete(
            task["id"]
        )

        self.selected_id = None

        self.refresh()