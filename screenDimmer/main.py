from tkinter import *
import ctypes
import keyboard
import threading
from PIL import Image, ImageDraw
import pystray

overlay = Tk()
overlay.title("Screen Dimmer")

overlay.configure(bg="black")
overlay.attributes("-alpha", 0.5)
overlay.attributes("-topmost", True)
overlay.overrideredirect(True)
overlay.geometry(f"{overlay.winfo_screenwidth()}x{overlay.winfo_screenheight()}+0+0")

# Make window click-through (Windows only)
overlay.update_idletasks()
hwnd = ctypes.windll.user32.GetParent(overlay.winfo_id())
style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20)

binding = False
brighten = 'alt+shift+up'

def rebind(event=None):
    global binding
    binding = True

    def set_keybind(key):
        print(f"Keybind set to: {key}")
        binding = False
        keybind_win.destroy()

    keybind_win = Tk()
    keybind_win.title("Set Keybind")
    keybind_win.geometry("300x300")
    keybind_win.configure(bg="white")
    Label(keybind_win, text="Change Keybinds:", bg="white").pack(pady=20)

    Button(keybind_win, text="A", command=lambda: set_keybind("a")).pack(pady=5)
    Button(keybind_win, text="B", command=lambda: set_keybind("b")).pack(pady=5)
    Button(keybind_win, text="Cancel", command=keybind_win.destroy).pack(pady=10)

def printKeys(event):
    print(event.name)

keyboard.on_press(rebind)
keyboard.on_press(printKeys)

def show_config():
    config_win = Tk()
    config_win.title("Config")
    config_win.geometry("300x200")
    config_win.configure(bg="white")
    Label(config_win, text="Config Window", bg="white").pack(pady=20)
    Button(config_win, text="Close", command=config_win.destroy).pack(pady=10)
    Button(config_win, text="Change Keybinds", command=rebind).pack(pady=10)

# Tray icon setup
def create_image():
    # Create a simple black circle icon
    image = Image.new('RGB', (64, 64), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 48, 48), fill=(50, 50, 50))
    return image

def on_open_config(icon, item):
    overlay.after(0, show_config)

tray_icon = None

def on_quit(icon, item):
    if icon:
        icon.stop()
    overlay.quit()
    import sys
    sys.exit()

def tray_thread():
    global tray_icon
    tray_icon = pystray.Icon(
        "ScreenDimmer",
        create_image(),
        "Screen Dimmer",
        menu=pystray.Menu(
            pystray.MenuItem("Config", on_open_config),
            pystray.MenuItem("Quit", on_quit)
        )
    )
    tray_icon.run()

threading.Thread(target=tray_thread, daemon=True).start()

overlay.mainloop()