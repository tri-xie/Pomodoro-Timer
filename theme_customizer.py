import customtkinter as ctk
from tkinter import filedialog
from themes import PRESETS

class ThemeCustomizer:
    def __init__(self, parent, timer):
        self.timer = timer
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Custom Themes")
        self.window.geometry("620x520")
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        self.window.withdraw()
        self.visible = False

        ctk.CTkLabel(self.window, text="Custom Themes", font=("Helvetica", 24, "bold")).pack(pady=(20,5))
        ctk.CTkLabel(self.window, text="Choose a preset color combination or your own background image").pack(pady=(0,12))

        self.choice = ctk.CTkOptionMenu(self.window, values=list(PRESETS), command=self.preview)
        self.choice.set(timer.theme_store.data.get("preset", "Classic"))
        self.choice.pack(pady=8)

        self.preview_box = ctk.CTkFrame(self.window, width=520, height=110)
        self.preview_box.pack(padx=35, pady=10, fill="x")
        self.preview_label = ctk.CTkLabel(self.preview_box, text="Theme preview", font=("Helvetica", 18, "bold"))
        self.preview_label.pack(expand=True)

        row = ctk.CTkFrame(self.window, fg_color="transparent")
        row.pack(pady=8)
        ctk.CTkButton(row, text="Choose Background Image", command=self.choose_image).pack(side="left", padx=5)
        ctk.CTkButton(row, text="Remove Image", command=self.remove_image).pack(side="left", padx=5)

        self.image_status = ctk.CTkLabel(self.window, text="")
        self.image_status.pack(pady=4)

        ctk.CTkButton(self.window, text="Apply Theme", command=self.apply).pack(pady=16)
        self.preview(self.choice.get())

    def show(self):
        self.choice.set(self.timer.theme_store.data.get("preset", "Classic"))
        self.preview(self.choice.get())
        path = self.timer.theme_store.data.get("background_image", "")
        self.image_status.configure(text=path if path else "No background image selected")
        self.window.deiconify(); self.window.lift(); self.visible = True

    def hide(self):
        self.window.withdraw(); self.visible = False

    def preview(self, name):
        c = PRESETS[name]
        self.preview_box.configure(fg_color=c["bg_start"])
        self.preview_label.configure(text_color=c["text"])

    def choose_image(self):
        path = filedialog.askopenfilename(
            title="Choose background image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.webp"), ("All files", "*.*")]
        )
        if path:
            self.timer.theme_store.set(background_image=path)
            self.image_status.configure(text=path)

    def remove_image(self):
        self.timer.theme_store.set(background_image="")
        self.image_status.configure(text="No background image selected")

    def apply(self):
        self.timer.theme_store.set(preset=self.choice.get())
        self.timer.apply_custom_theme()
        self.hide()
