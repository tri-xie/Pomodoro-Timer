import json
import uuid
from datetime import datetime, timedelta


class TaskStore:

    def __init__(
        self,
        path
    ):

        self.path = path
        self.tasks = []

        self.load()

    # ======================================================
    # LOAD
    # ======================================================

    def load(self):

        try:

            with open(
                self.path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            self.tasks = (
                data
                if isinstance(data, list)
                else []
            )

            # ------------------------------------------------
            # Make older tasks compatible with the new
            # scheduler format.
            # ------------------------------------------------

            changed = False

            for task in self.tasks:

                if "schedule_type" not in task:

                    task["schedule_type"] = "once"
                    changed = True

                if "active" not in task:

                    task["active"] = not task.get(
                        "completed",
                        False
                    )

                    changed = True

                if "days" not in task:

                    task["days"] = []
                    changed = True

                if "notified" not in task:

                    task["notified"] = False
                    changed = True

                if "last_notified" not in task:

                    task["last_notified"] = None
                    changed = True

            if changed:

                self.save()

        except (
            FileNotFoundError,
            json.JSONDecodeError,
            OSError
        ):

            self.tasks = []

    # ======================================================
    # SAVE
    # ======================================================

    def save(self):

        try:

            with open(
                self.path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    self.tasks,
                    f,
                    indent=2
                )

        except OSError:

            pass

    # ======================================================
    # ADD TASK
    # ======================================================

    def add(
        self,
        title,
        scheduled_for,
        duration_minutes,
        schedule_type="once",
        days=None
    ):

        if days is None:

            days = []

        item = {

            "id":
                str(uuid.uuid4()),

            "title":
                title.strip(),

            "scheduled_for":
                scheduled_for,

            "duration_minutes":
                int(duration_minutes),

            "completed":
                False,

            "active":
                True,

            "schedule_type":
                schedule_type,

            "days":
                list(days),

            "notified":
                False,

            "last_notified":
                None,

            "created_at":
                datetime.now().isoformat(
                    timespec="seconds"
                ),
        }

        self.tasks.append(
            item
        )

        self.save()

        return item

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        task_id,
        **changes
    ):

        for item in self.tasks:

            if item.get("id") == task_id:

                item.update(
                    changes
                )

                self.save()

                return item

        return None

    # ======================================================
    # DELETE
    # ======================================================

    def delete(
        self,
        task_id
    ):

        self.tasks = [

            task

            for task in self.tasks

            if task.get("id") != task_id

        ]

        self.save()

    # ======================================================
    # ACTIVATE / DEACTIVATE
    # ======================================================

    def set_active(
        self,
        task_id,
        active
    ):

        return self.update(
            task_id,
            active=bool(active)
        )

    # ======================================================
    # GET TASK
    # ======================================================

    def get(
        self,
        task_id
    ):

        for task in self.tasks:

            if task.get("id") == task_id:

                return task

        return None

    # ======================================================
    # PARSE SCHEDULED DATETIME
    # ======================================================

    def _parse_datetime(
        self,
        value
    ):

        try:

            return datetime.fromisoformat(
                value
            )

        except (
            ValueError,
            TypeError
        ):

            return None

    # ======================================================
    # NEXT RECURRING OCCURRENCE
    # ======================================================

    def next_occurrence(
        self,
        task,
        from_time=None
    ):

        if from_time is None:

            from_time = datetime.now()

        schedule_type = task.get(
            "schedule_type",
            "once"
        )

        scheduled = self._parse_datetime(
            task.get(
                "scheduled_for"
            )
        )

        if scheduled is None:

            return None

        # --------------------------------------------------
        # One-time task
        # --------------------------------------------------

        if schedule_type == "once":

            if task.get(
                "completed",
                False
            ):

                return None

            return scheduled

        # --------------------------------------------------
        # Recurring task
        # --------------------------------------------------

        if not task.get(
            "active",
            True
        ):

            return None

        days = task.get(
            "days",
            []
        )

        if not days:

            return None

        # Python weekday:
        #
        # Monday = 0
        # Tuesday = 1
        # ...
        # Sunday = 6
        #
        # Stored days use these same numbers.
        # --------------------------------------------------

        for offset in range(
            0,
            8
        ):

            candidate_date = (
                from_time.date()
                + timedelta(
                    days=offset
                )
            )

            if candidate_date.weekday() not in days:

                continue

            candidate = datetime.combine(
                candidate_date,
                scheduled.time()
            )

            if candidate >= from_time:

                return candidate

        return None

    # ======================================================
    # UPCOMING
    # ======================================================

    def upcoming(self):

        now = datetime.now()

        result = []

        for task in self.tasks:

            if task.get(
                "completed",
                False
            ):

                continue

            if (
                task.get(
                    "schedule_type",
                    "once"
                ) == "once"
            ):

                if task.get(
                    "notified",
                    False
                ):

                    # A one-time task that has already
                    # notified remains available for the
                    # user to start manually.
                    result.append(
                        task
                    )

                    continue

                occurrence = self.next_occurrence(
                    task,
                    now
                )

                if occurrence is not None:

                    result.append(
                        task
                    )

                continue

            # ------------------------------------------------
            # Recurring
            # ------------------------------------------------

            if not task.get(
                "active",
                True
            ):

                continue

            occurrence = self.next_occurrence(
                task,
                now
            )

            if occurrence is not None:

                result.append(
                    task
                )

        result.sort(
            key=lambda item: (
                self.display_datetime(
                    item
                )
                or datetime.max
            )
        )

        return result

    # ======================================================
    # ALL SCHEDULES
    # ======================================================

    def all_schedules(self):

        return sorted(
            [
                task

                for task in self.tasks

                if not task.get(
                    "completed",
                    False
                )
            ],
            key=lambda item: (
                self.display_datetime(
                    item
                )
                or datetime.max
            )
        )

    # ======================================================
    # DISPLAY DATETIME
    # ======================================================

    def display_datetime(
        self,
        task
    ):

        schedule_type = task.get(
            "schedule_type",
            "once"
        )

        if schedule_type == "once":

            return self._parse_datetime(
                task.get(
                    "scheduled_for"
                )
            )

        return self.next_occurrence(
            task
        )

    # ======================================================
    # CHECK DUE SCHEDULES
    # ======================================================

    def due_tasks(self):

        now = datetime.now()

        due = []

        for task in self.tasks:

            if task.get(
                "completed",
                False
            ):

                continue

            if not task.get(
                "active",
                True
            ):

                continue

            schedule_type = task.get(
                "schedule_type",
                "once"
            )

            # ------------------------------------------------
            # ONE-TIME
            # ------------------------------------------------

            if schedule_type == "once":

                if task.get(
                    "notified",
                    False
                ):

                    continue

                scheduled = self._parse_datetime(
                    task.get(
                        "scheduled_for"
                    )
                )

                if (
                    scheduled is not None
                    and now >= scheduled
                ):

                    due.append(
                        task
                    )

                continue

            # ------------------------------------------------
            # RECURRING
            # ------------------------------------------------

            occurrence = self.next_occurrence(
                task,
                now - timedelta(
                    seconds=1
                )
            )

            if occurrence is None:

                continue

            if now >= occurrence:

                occurrence_key = (
                    occurrence.isoformat(
                        timespec="minutes"
                    )
                )

                if task.get(
                    "last_notified"
                ) != occurrence_key:

                    due.append(
                        task
                    )

        return due

    # ======================================================
    # MARK NOTIFIED
    # ======================================================

    def mark_notified(
        self,
        task
    ):

        schedule_type = task.get(
            "schedule_type",
            "once"
        )

        if schedule_type == "once":

            task["notified"] = True

        else:

            occurrence = self.next_occurrence(
                task,
                datetime.now()
                - timedelta(
                    seconds=1
                )
            )

            if occurrence is not None:

                task["last_notified"] = (
                    occurrence.isoformat(
                        timespec="minutes"
                    )
                )

        self.save()

    # ======================================================
    # COMPLETE ONE-TIME TASK
    # ======================================================

    def complete_one_time(
        self,
        task_id
    ):

        task = self.get(
            task_id
        )

        if task is None:

            return None

        if task.get(
            "schedule_type",
            "once"
        ) == "once":

            task["completed"] = True
            task["active"] = False

            self.save()

        return task