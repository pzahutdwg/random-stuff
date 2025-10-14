from tkinter import *
import ctypes

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

overlay.mainloop()