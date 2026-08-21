import customtkinter as ctk
from tkinter import Canvas


class StatsPanel:
    def __init__(self, parent, timer):
        self.timer = timer
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Productivity Dashboard")
        self.window.geometry("980x820")
        self.window.minsize(900, 740)
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        self.window.withdraw()
        self.visible = False

        ctk.CTkLabel(
            self.window,
            text="Productivity Dashboard",
            font=("Helvetica", 25, "bold")
        ).pack(pady=(16, 3))

        controls = ctk.CTkFrame(
            self.window,
            fg_color="transparent"
        )
        controls.pack(
            fill="x",
            padx=20,
            pady=(0, 8)
        )

        self.period = ctk.CTkSegmentedButton(
            controls,
            values=["Daily", "Weekly"],
            command=self.refresh
        )

        self.period.set("Daily")
        self.period.pack(side="left")

        ctk.CTkButton(
            controls,
            text="Clear History",
            width=120,
            command=self.clear_history
        ).pack(side="right")

        self.cards = ctk.CTkFrame(
            self.window,
            fg_color="transparent"
        )

        self.cards.pack(
            fill="x",
            padx=20,
            pady=5
        )

        for i in range(5):
            self.cards.grid_columnconfigure(
                i,
                weight=1
            )

        self.streak = self._card(
            0,
            "Current streak"
        )

        self.best = self._card(
            1,
            "Best day"
        )

        self.rate = self._card(
            2,
            "Focus rate"
        )

        self.today = self._card(
            3,
            "Today's goal"
        )

        self.total = self._card(
            4,
            "Total focus"
        )

        self.chart_frame = ctk.CTkFrame(
            self.window
        )

        self.chart_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=8
        )

        ctk.CTkLabel(
            self.window,
            text="Activity heatmap",
            font=("Helvetica", 17, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(6, 2)
        )

        self.heatmap = Canvas(
            self.window,
            height=115,
            highlightthickness=0
        )

        self.heatmap.pack(
            fill="x",
            padx=20,
            pady=(0, 8)
        )

        ctk.CTkLabel(
            self.window,
            text="Recent sessions",
            font=("Helvetica", 17, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(4, 3)
        )

        self.history_box = ctk.CTkTextbox(
            self.window,
            height=120
        )

        self.history_box.pack(
            fill="x",
            padx=20,
            pady=(0, 12)
        )

    # ======================================================
    # STAT CARDS
    # ======================================================

    def _card(
        self,
        col,
        label
    ):

        frame = ctk.CTkFrame(
            self.cards
        )

        frame.grid(
            row=0,
            column=col,
            padx=4,
            sticky="nsew"
        )

        ctk.CTkLabel(
            frame,
            text=label,
            font=("Helvetica", 12)
        ).pack(
            pady=(8, 1)
        )

        value = ctk.CTkLabel(
            frame,
            text="0",
            font=("Helvetica", 18, "bold")
        )

        value.pack(
            pady=(0, 8)
        )

        return value

    # ======================================================
    # SHOW / HIDE
    # ======================================================

    def show(self):

        self.refresh()

        self.window.deiconify()
        self.window.lift()

        self.visible = True

    def hide(self):

        self.window.withdraw()

        self.visible = False

    # ======================================================
    # REFRESH
    # ======================================================

    def refresh(
        self,
        *_
    ):

        mode = self.period.get()

        rows = (
            self.timer.history.daily_stats(7)
            if mode == "Daily"
            else self.timer.history.weekly_stats(8)
        )

        analytics = self.timer.history.analytics(
            daily_goal=4
        )

        focus = sum(
            r["focus_minutes"]
            for r in rows
        )

        sessions = sum(
            r["sessions"]
            for r in rows
        )

        best = analytics["best_day"]

        self.streak.configure(
            text=f"{analytics['streak_days']} day(s)"
        )

        self.best.configure(
            text=(
                f"{best['sessions']} sessions"
                if best
                else "—"
            )
        )

        self.rate.configure(
            text=f"{analytics['completion_rate']:.0f}%"
        )

        self.today.configure(
            text=(
                f"{analytics['today_sessions']}/"
                f"{analytics['daily_goal']}"
            )
        )

        self.total.configure(
            text=f"{focus // 60}h {focus % 60:02d}m"
        )

        self._draw_chart(
            rows,
            mode
        )

        self._draw_heatmap(
            analytics["by_day"]
        )

        self._refresh_history()

    # ======================================================
    # CHART
    # ======================================================

    def _draw_chart(
        self,
        rows,
        mode
    ):

        for child in self.chart_frame.winfo_children():

            child.destroy()

        canvas = Canvas(
            self.chart_frame,
            highlightthickness=0,
            bg=self._bg(),
            height=260
        )

        canvas.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=8
        )

        canvas.bind(
            "<Configure>",
            lambda e: self._paint_chart(
                canvas,
                rows,
                mode
            )
        )

    def _paint_chart(
        self,
        canvas,
        rows,
        mode
    ):

        canvas.delete("all")

        width = max(
            canvas.winfo_width(),
            500
        )

        height = max(
            canvas.winfo_height(),
            240
        )

        values = [
            r["focus_minutes"]
            for r in rows
        ]

        labels = [
            r["label"]
            for r in rows
        ]

        maximum = max(
            max(values) if values else 0,
            60
        )

        left = 55
        right = 25
        top = 25
        bottom = 40

        plot_w = width - left - right
        plot_h = height - top - bottom

        for i in range(5):

            y = (
                top
                + plot_h
                - plot_h * i / 4
            )

            canvas.create_line(
                left,
                y,
                width - right,
                y,
                fill="#9A9A9A",
                dash=(2, 4)
            )

            canvas.create_text(
                left - 8,
                y,
                text=f"{int(maximum * i / 4)}m",
                anchor="e",
                fill=self._text(),
                font=("Helvetica", 9)
            )

        n = len(rows) or 1

        slot = plot_w / n

        bw = max(
            12,
            slot * .58
        )

        for i, (
            label,
            value
        ) in enumerate(
            zip(
                labels,
                values
            )
        ):

            x = (
                left
                + slot * i
                + slot / 2
            )

            y0 = top + plot_h

            y1 = (
                y0
                - plot_h * value / maximum
            )

            canvas.create_rectangle(
                x - bw / 2,
                y1,
                x + bw / 2,
                y0,
                fill="#3B82F6",
                outline=""
            )

            canvas.create_text(
                x,
                y1 - 5 if value else y0 + 4,
                text=str(value),
                fill=self._text(),
                font=("Helvetica", 9),
                anchor="s" if value else "n"
            )

            canvas.create_text(
                x,
                height - 16,
                text=label,
                fill=self._text(),
                font=("Helvetica", 9)
            )

        title = (
            "Focus time by day"
            if mode == "Daily"
            else "Focus time by week"
        )

        canvas.create_text(
            left,
            6,
            text=title,
            anchor="nw",
            fill=self._text(),
            font=("Helvetica", 12, "bold")
        )

    # ======================================================
    # HEATMAP
    # ======================================================

    def _draw_heatmap(
        self,
        by_day
    ):

        self.heatmap.delete("all")

        self.heatmap.configure(
            bg=self._bg()
        )

        from datetime import (
            date,
            timedelta
        )

        today = date.today()

        start = (
            today
            - timedelta(days=83)
        )

        cell = 12
        gap = 3

        for i in range(84):

            day = (
                start
                + timedelta(days=i)
            )

            count = by_day.get(
                day.isoformat(),
                0
            )

            x = (
                (i // 7)
                * (cell + gap)
                + 30
            )

            y = (
                (i % 7)
                * (cell + gap)
                + 10
            )

            fills = [
                "#E5E7EB",
                "#BFDBFE",
                "#93C5FD",
                "#60A5FA",
                "#2563EB"
            ]

            fill = fills[
                min(
                    count,
                    4
                )
            ]

            self.heatmap.create_rectangle(
                x,
                y,
                x + cell,
                y + cell,
                fill=fill,
                outline=""
            )

        self.heatmap.create_text(
            2,
            10,
            text="12 wk",
            anchor="nw",
            fill=self._text(),
            font=("Helvetica", 9)
        )

    # ======================================================
    # SESSION HISTORY
    # ======================================================

    def _refresh_history(self):

        self.history_box.configure(
            state="normal"
        )

        self.history_box.delete(
            "1.0",
            "end"
        )

        for item in reversed(
            self.timer.history.sessions[-30:]
        ):

            if item.get("completed"):

                self.history_box.insert(
                    "end",
                    f"{item.get('timestamp', '')} | "
                    f"{item.get('type', '')} | "
                    f"{item.get('duration_minutes', 0)} min\n"
                )

        self.history_box.configure(
            state="disabled"
        )

    # ======================================================
    # CLEAR HISTORY CONFIRMATION
    # ======================================================

    def clear_history(self):

        confirmation = ctk.CTkToplevel(
            self.window
        )

        confirmation.title(
            "Clear History"
        )

        confirmation.geometry(
            "400x210"
        )

        confirmation.resizable(
            False,
            False
        )

        confirmation.transient(
            self.window
        )

        confirmation.grab_set()

        confirmation.lift()

        # Center the confirmation window.
        self.window.update_idletasks()

        parent_x = self.window.winfo_x()
        parent_y = self.window.winfo_y()

        parent_width = self.window.winfo_width()
        parent_height = self.window.winfo_height()

        width = 400
        height = 210

        x = (
            parent_x
            + (parent_width - width) // 2
        )

        y = (
            parent_y
            + (parent_height - height) // 2
        )

        confirmation.geometry(
            f"{width}x{height}+{x}+{y}"
        )

        # Title
        ctk.CTkLabel(
            confirmation,
            text="Clear Session History?",
            font=(
                "Helvetica",
                20,
                "bold"
            )
        ).pack(
            pady=(25, 8)
        )

        # Warning message
        ctk.CTkLabel(
            confirmation,
            text=(
                "Are you sure you want to permanently\n"
                "delete all your session history?"
            ),
            font=(
                "Helvetica",
                14
            ),
            justify="center"
        ).pack(
            pady=(0, 20)
        )

        # Buttons
        button_frame = ctk.CTkFrame(
            confirmation,
            fg_color="transparent"
        )

        button_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 20)
        )

        button_frame.grid_columnconfigure(
            0,
            weight=1
        )

        button_frame.grid_columnconfigure(
            1,
            weight=1
        )

        # Cancel button
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=confirmation.destroy
        ).grid(
            row=0,
            column=0,
            padx=(0, 6),
            sticky="ew"
        )

        # Confirm button
        ctk.CTkButton(
            button_frame,
            text="Clear",
            fg_color="#E74C3C",
            hover_color="#C0392B",
            command=lambda: self._confirm_clear_history(
                confirmation
            )
        ).grid(
            row=0,
            column=1,
            padx=(6, 0),
            sticky="ew"
        )

        confirmation.protocol(
            "WM_DELETE_WINDOW",
            confirmation.destroy
        )

    def _confirm_clear_history(
        self,
        confirmation
    ):

        # Close the confirmation window first.
        confirmation.destroy()

        # Permanently clear the saved history.
        self.timer.history.clear()

        # Refresh the dashboard.
        self.refresh()

    # ======================================================
    # THEME HELPERS
    # ======================================================

    def _bg(self):

        return self.window._apply_appearance_mode(
            self.window._fg_color
        )

    def _text(self):

        return (
            "#111111"
            if ctk.get_appearance_mode() == "Light"
            else "#F2F2F2"
        )