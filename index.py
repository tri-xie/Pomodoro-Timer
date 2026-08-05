import tkinter as tk
import customtkinter as ctk


def show_splash_screen(root, delay=2200):
    root.withdraw()
    splash = tk.Toplevel(root)
    splash.overrideredirect(True)
    splash.config(bg="#f7f5dd")

    width, height = 340, 220
    x = (splash.winfo_screenwidth() - width) // 2
    y = (splash.winfo_screenheight() - height) // 2
    splash.geometry(f"{width}x{height}+{x}+{y}")

    tk.Label(
        splash,
        text="Pomodoro Timer",
        fg="#9bdeac",
        bg="#f7f5dd",
        font=("Courier", 28, "bold"),
    ).pack(pady=(30, 8))

    dot_label = tk.Label(
        splash,
        text="•   •   •",
        fg="#e7305b",
        bg="#f7f5dd",
        font=("Courier", 36, "bold"),
    )
    dot_label.pack(pady=8)

    status_label = tk.Label(
        splash,
        text="Loading...",
        fg="#333333",
        bg="#f7f5dd",
        font=("Courier", 12),
    )
    status_label.pack(pady=(4, 24))

    def animate_dots(frame=0):
        pattern = [
            "•       ",
            "  •     ",
            "    •   ",
            "      • ",
            "    •   ",
            "  •     ",
        ]
        dot_label.config(text=pattern[frame % len(pattern)])
        status_label.config(text=f"Loading{'.' * ((frame // 2) % 4)}")
        splash.after(140, animate_dots, frame + 1)

    animate_dots()
    root.after(delay, lambda: (splash.destroy(), root.deiconify()))


# Window creation
app = ctk.CTk()
app.title("Pomodoro : Keep Focused")
app.geometry("400x600")
app.resizable(False, False)

show_splash_screen(app)

label = ctk.CTkLabel(app, text="Ready to focus!", font=ctk.CTkFont(size=22, weight="bold"))
label.pack(pady=40)

app.mainloop()
