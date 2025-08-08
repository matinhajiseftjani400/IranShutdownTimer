import customtkinter as ctk
import threading
import subprocess
import sys
import time
from tkinter import messagebox
from datetime import datetime, timedelta
import pystray
from PIL import Image

stop_flag = False
icon = None

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def close_program(app=None):
    global stop_flag
    stop_flag = True
    if icon:
        icon.stop()
    if app:
        app.destroy()
    sys.exit(0)


def show_warning(app):
    messagebox.showinfo(
        "⚠️ هشدار خاموشی",
        "⏳ زمان خاموشی رسیده!\nبا زدن دکمه 'باشه' سیستم به حالت Hibernate میره.")
    try:
        subprocess.run(["C:\\Windows\\System32\\shutdown.exe", "/h"], check=True)
    except Exception as e:
        messagebox.showerror("خطا", f"خطا هنگام خاموش کردن سیستم:\n{str(e)}")
    close_program(app)


def start_timer(shutdown_time_str, warning_minutes_str, app):
    global stop_flag

    try:
        shutdown_time = datetime.strptime(shutdown_time_str, "%H:%M").time()
        warning_minutes = int(warning_minutes_str)

        now = datetime.now()
        shutdown_dt = now.replace(hour=shutdown_time.hour, minute=shutdown_time.minute, second=0, microsecond=0)
        if shutdown_dt < now:
            shutdown_dt += timedelta(days=1)

        warning_time = shutdown_dt - timedelta(minutes=warning_minutes)

        def countdown():
            while not stop_flag:
                now = datetime.now()
                remaining = warning_time - now
                if remaining.total_seconds() <= 0:
                    show_warning(app)
                    break
                time.sleep(1)

        threading.Thread(target=countdown, daemon=True).start()

    except Exception as e:
        messagebox.showerror("خطا", f"مشکلی پیش اومد:\n{str(e)}")
        close_program(app)


def create_image():
    # بارگذاری تصویر آیکن برای System Tray
    return Image.open("img/flash.png")


def run_tray_icon(app):
    global icon
    menu = pystray.Menu(
        pystray.MenuItem("خروج", lambda: close_program(app))
    )
    icon = pystray.Icon("shutdown_timer", create_image(), "زمان خاموشی", menu)
    threading.Thread(target=icon.run, daemon=True).start()


def center_window(window, width=400, height=420):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


app = ctk.CTk()
center_window(app, 400, 420)
app.title("⏱️ زمان خاموشی ایرانی 😄")

# ست کردن آیکن پنجره
app.iconbitmap("img/flash.ico")

title_label = ctk.CTkLabel(app, text="💡سلام ایرانی! برق کی می‌ره؟", font=("B Nazanin", 20))
title_label.pack(pady=20)

time_entry = ctk.CTkEntry(app, placeholder_text="22:45 مثلا", width=250)
time_entry.pack(pady=10)

warning_entry = ctk.CTkEntry(app, placeholder_text="بدم؟ قبل چند دقیقه هشدار", width=250)
warning_entry.pack(pady=10)


def on_start():
    time_str = time_entry.get()
    warn_str = warning_entry.get()
    if not time_str or not warn_str:
        messagebox.showwarning("خطا", "هر دو فیلد رو پر کن!")
        return
    start_button.configure(state="disabled", text="⏳ مخفی شد...")
    run_tray_icon(app)
    start_timer(time_str, warn_str, app)
    app.withdraw()  # مخفی کردن پنجره


start_button = ctk.CTkButton(app, text="شروع ✅", command=on_start)
start_button.pack(pady=20)

exit_button = ctk.CTkButton(app, text="خروج ❌", fg_color="red", command=lambda: close_program(app))
exit_button.pack(pady=10)

app.mainloop()