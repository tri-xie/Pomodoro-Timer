import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk

import config
from timer import PomodoroTimer


# ==========================================================
# CUSTOMTKINTER SETUP
# ==========================================================

ctk.set_default_color_theme("blue")


# ==========================================================
# MAIN APPLICATION WINDOW
# ==========================================================

app = ctk.CTk()

app.title("Pomodoro : Keep Focused")

app.geometry("420x700")

app.minsize(
    420,
    700
)

# Allow the window to be resized and maximized.
app.resizable(
    True,
    True
)


# ==========================================================
# APPLICATION ICON
# ==========================================================

try:

    app.iconbitmap(
        config.ICON_PATH
    )

except Exception as error:

    print(
        f"Could not load application icon: {error}"
    )


# ==========================================================
# LOAD SPLASH LOGO
# ==========================================================

try:

    logo_image = Image.open(
        config.LOGO_PATH
    )

    logo_photo = ImageTk.PhotoImage(
        logo_image.resize(
            (120, 120),
            Image.Resampling.LANCZOS
        ),
        master=app
    )

except Exception as error:

    print(
        f"Could not load splash logo: {error}"
    )

    logo_photo = None


# ==========================================================
# HIDE MAIN WINDOW DURING STARTUP
# ==========================================================

app.withdraw()

app.timer = None


# ==========================================================
# SPLASH SCREEN
# ==========================================================

class SplashScreen:

    def __init__(
        self,
        main
    ):

        self.master = main

        self.animation_id = None

        self.window = ctk.CTkToplevel(
            main
        )

        # Keep the splash hidden while it is being built.
        self.window.withdraw()

        self.window.overrideredirect(
            True
        )

        self.window.configure(
            fg_color=config.BG_COLOR
        )

        # --------------------------------------------------
        # SPLASH WINDOW SIZE
        # --------------------------------------------------

        window_width = 450
        window_height = 300

        screen_width = (
            self.window.winfo_screenwidth()
        )

        screen_height = (
            self.window.winfo_screenheight()
        )

        center_x = int(
            (screen_width / 2)
            - (window_width / 2)
        )

        center_y = int(
            (screen_height / 2)
            - (window_height / 2)
        )

        self.window.geometry(
            f"{window_width}x{window_height}"
            f"+{center_x}+{center_y}"
        )

        # --------------------------------------------------
        # LOGO
        # --------------------------------------------------

        self.logo_label = tk.Label(
            self.window,
            image=logo_photo,
            bg=config.BG_COLOR,
            borderwidth=0,
            highlightthickness=0
        )

        # Keep a reference to prevent garbage collection.
        self.logo_label.image = logo_photo

        self.logo_label.pack(
            expand=True,
            pady=(40, 0)
        )

        # --------------------------------------------------
        # TITLE
        # --------------------------------------------------

        self.title_label = tk.Label(
            self.window,
            text="POMODORO TIMER",
            fg=config.TEXT_COLOR,
            bg=config.BG_COLOR,
            font=(
                "Helvetica",
                24,
                "bold"
            ),
            justify="center"
        )

        self.title_label.pack(
            expand=True
        )

        # --------------------------------------------------
        # SUBTITLE
        # --------------------------------------------------

        self.subtitle_label = tk.Label(
            self.window,
            text="Keep Focused",
            fg=config.TEXT_COLOR,
            bg=config.BG_COLOR,
            font=(
                "Helvetica",
                14,
                "italic"
            ),
            justify="center"
        )

        self.subtitle_label.pack(
            expand=True
        )

        # --------------------------------------------------
        # STATUS
        # --------------------------------------------------

        self.status_label = tk.Label(
            self.window,
            text="Loading engine.",
            fg=config.BREAK_COLOR,
            bg=config.BG_COLOR,
            font=(
                "Helvetica",
                12,
                "italic"
            )
        )

        self.status_label.pack(
            expand=True,
            pady=(0, 40)
        )

        # --------------------------------------------------
        # FINISH BUILDING BEFORE SHOWING
        # --------------------------------------------------

        self.window.update_idletasks()

        self.window.deiconify()

        self.window.lift()

        # --------------------------------------------------
        # START ANIMATION
        # --------------------------------------------------

        self.animate_dots(
            0
        )

        # Show splash screen for 3 seconds.
        self.window.after(
            3000,
            self.terminate_splash
        )


    def animate_dots(
        self,
        count
    ):

        if not self.window.winfo_exists():
            return

        dots = "." * (
            count % 4
        )

        self.status_label.config(
            text=f"Loading engine{dots}"
        )

        self.animation_id = (
            self.window.after(
                400,
                self.animate_dots,
                count + 1
            )
        )


    def terminate_splash(self):

        # Stop the loading animation.
        if self.animation_id is not None:

            try:

                self.window.after_cancel(
                    self.animation_id
                )

            except Exception:

                pass

            self.animation_id = None

        # Destroy the splash window first.
        if self.window.winfo_exists():

            try:

                self.window.destroy()

            except Exception:

                pass

        # Build the main application while the
        # main window is still hidden.
        launch_main_app()


# ==========================================================
# SAVE SETTINGS AND CLOSE APPLICATION
# ==========================================================

def save_settings_and_close():

    try:

        # Check that the timer was successfully created.
        if (
            hasattr(app, "timer")
            and app.timer is not None
        ):

            app.timer.save_settings()

            # Cleanly destroy child windows before
            # destroying the main application window.
            scheduler_panel = getattr(
                app.timer,
                "scheduler_panel",
                None
            )

            if scheduler_panel is not None:

                try:

                    if scheduler_panel.window.winfo_exists():

                        scheduler_panel.window.destroy()

                except Exception:

                    pass

    except Exception as error:

        print(
            f"Could not save settings: {error}"
        )

    finally:

        try:

            app.destroy()

        except Exception:

            pass


# ==========================================================
# SHOW FINISHED MAIN APPLICATION
# ==========================================================

def show_main_app():

    try:

        # Make sure all pending geometry calculations
        # are completed before showing the window.
        app.update_idletasks()

        app.deiconify()

        app.lift()

        app.focus_force()

    except Exception as error:

        print(
            f"Could not show main application: {error}"
        )


# ==========================================================
# LAUNCH MAIN APPLICATION
# ==========================================================

def launch_main_app():

    try:

        # --------------------------------------------------
        # IMPORTANT:
        #
        # Build PomodoroTimer while the main application
        # window is still hidden.
        #
        # This prevents the empty/glitching window from
        # briefly appearing before the interface is ready.
        # --------------------------------------------------

        app.timer = PomodoroTimer(
            app
        )

        # Handle the X / Close button.
        app.protocol(
            "WM_DELETE_WINDOW",
            save_settings_and_close
        )

        # --------------------------------------------------
        # Show the window only after CustomTkinter and Tk
        # have finished processing all pending UI updates.
        # --------------------------------------------------

        app.after_idle(
            show_main_app
        )

    except Exception as error:

        print(
            f"Could not launch application: {error}"
        )

        # If startup fails, show the main window so the
        # application does not remain permanently hidden.
        app.after_idle(
            show_main_app
        )


# ==========================================================
# START APPLICATION
# ==========================================================

if __name__ == "__main__":

    SplashScreen(
        app
    )

    app.mainloop()