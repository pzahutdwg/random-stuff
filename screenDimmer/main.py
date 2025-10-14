from tkinter import *
import ctypes
import keyboard
import threading
from PIL import Image, ImageDraw
import pystray
# import sys

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
brighter = 'alt+shift+up'
darker = 'alt+shift+down'

def normalize_keysym(keysym: str) -> str:
    """Normalize common modifier/key names to nicer labels."""
    mapping = {
        'Alt_L': 'Alt', 'Alt_R': 'Alt', 'Control_L': 'Ctrl', 'Control_R': 'Ctrl',
        'Shift_L': 'Shift', 'Shift_R': 'Shift', 'Return': 'Enter', 'Escape': 'Esc',
        'Left': 'Left', 'Right': 'Right', 'Up': 'Up', 'Down': 'Down'
    }
    return mapping.get(keysym, keysym).lower()

def format_combo(parts):
    # Keep a consistent ordering: ctrl/alt/shift then others
    order = {'ctrl': 0, 'alt': 1, 'shift': 2}
    parts = [p for p in parts if p]
    parts_sorted = sorted(parts, key=lambda p: order.get(p, 10))
    return "+".join(parts_sorted)

def rebind(event=None):
    """Open a small config window to choose which action to rebind, then capture keys."""
    # parent Toplevel for config
    cfg = Toplevel(overlay)
    cfg.title("Change Keybinds")
    cfg.geometry("340x220")
    cfg.configure(bg="white")
    cfg.transient(overlay)
    cfg.grab_set()

    Label(cfg, text="Change Keybinds:", bg="white", font=(None, 12, 'bold')).pack(pady=10)

    # Buttons that will be updated when bindings change
    brighter_btn = Button(cfg, text=f"Make Brighter ({brighter})")
    darker_btn = Button(cfg, text=f"Make Darker ({darker})")

    def capture_for(action, button):
        # modal to capture key combo
        cap = Toplevel(cfg)
        cap.title(f"Set keybind for {action}")
        cap.geometry("420x160")
        cap.configure(bg="white")
        cap.transient(cfg)
        cap.grab_set()

        info = Label(cap, text="Press the desired keys. Press Enter to confirm, Esc to cancel.", bg="white")
        info.pack(pady=8)
        combo_var = StringVar(value="")
        combo_label = Label(cap, textvariable=combo_var, bg="white", font=(None, 12))
        combo_label.pack(pady=8)

        pressed = set()

        def on_key_press(e):
            k = normalize_keysym(e.keysym)
            pressed.add(k)
            combo_var.set(format_combo(sorted(pressed)))

        def on_key_release(e):
            k = normalize_keysym(e.keysym)
            # don't remove modifiers immediately to allow combos that include them
            if k not in ('ctrl', 'alt', 'shift') and k in pressed:
                # non-modifier keys may be removed on release
                pressed.discard(k)
            combo_var.set(format_combo(sorted(pressed)))

        def on_confirm(e=None):
            combo = combo_var.get()
            if not combo:
                return
            # update the module-level bindings
            global brighter, darker
            if action == 'brighter':
                brighter = combo
                button.config(text=f"Make Brighter ({brighter})")
            else:
                darker = combo
                button.config(text=f"Make Darker ({darker})")
            # re-register hotkeys so the new binding becomes active immediately
            try:
                register_hotkeys()
            except Exception:
                pass
            cap.unbind('<KeyPress>')
            cap.unbind('<KeyRelease>')
            cap.destroy()

        def on_cancel(e=None):
            cap.unbind('<KeyPress>')
            cap.unbind('<KeyRelease>')
            cap.destroy()

        cap.bind('<KeyPress>', on_key_press)
        cap.bind('<KeyRelease>', on_key_release)
        cap.bind('<Return>', on_confirm)
        cap.bind('<Escape>', on_cancel)
        cap.focus_set()

    brighter_btn.config(command=lambda: capture_for('brighter', brighter_btn))
    darker_btn.config(command=lambda: capture_for('darker', darker_btn))

    brighter_btn.pack(pady=6)
    darker_btn.pack(pady=6)
    Button(cfg, text='Close', command=cfg.destroy).pack(pady=12)

keys = {}

def keyEvent(event):
    keys[event.name] = True

def release(event):
    keys[event.name] = False

def keyboard_event_handler(event):
    if event.event_type == 'down':
        keyEvent(event)
    elif event.event_type == 'up':
        release(event)

keyboard.hook(keyboard_event_handler)

def show_config():
    config_win = Tk()
    config_win.title("Config")
    config_win.geometry("300x200")
    config_win.configure(bg="white")
    config_win.attributes("-topmost", True)
    Label(config_win, text="Config Window", bg="white").pack(pady=20)
    Button(config_win, text="Close", command=config_win.destroy).pack(pady=10)
    Button(config_win, text="Change Keybinds", command=rebind).pack(pady=10)

# Opacity control
_opacity_step = 0.05
def clamp_alpha(a: float) -> float:
    return max(0.0, min(1.0, a))

def apply_opacity(value: float):
    overlay.attributes('-alpha', value)

def make_brighter():
    try:
        current = float(overlay.attributes('-alpha'))
    except Exception:
        current = 0.5
    # To make the screen brighter we need to make the overlay more transparent
    # (lower alpha). Subtract the step from the current alpha.
    new = clamp_alpha(current - _opacity_step)
    apply_opacity(new)
    # print(f"Opacity decreased to {new} (brighter screen)")

def make_darker():
    try:
        current = float(overlay.attributes('-alpha'))
    except Exception:
        current = 0
    # To make the screen darker we need to make the overlay more opaque
    # (higher alpha). Add the step to the current alpha.
    new = clamp_alpha(current + _opacity_step)
    apply_opacity(new)
    # print(f"Opacity increased to {new} (darker screen)")

# Global hotkey management using `keyboard` module
_registered_hotkeys = []

def _hotkey_to_keyboard_combo(combo: str) -> str:
    # stored combos are like 'ctrl+alt+up' — keyboard expects e.g. 'ctrl+alt+up'
    return combo.replace(' ', '')

def register_hotkeys():
    global _registered_hotkeys
    # unregister previous
    for hk in _registered_hotkeys:
        try:
            keyboard.remove_hotkey(hk)
        except Exception:
            pass
    _registered_hotkeys = []
    # Register new hotkeys if valid
    try:
        if brighter:
            hk = keyboard.add_hotkey(_hotkey_to_keyboard_combo(brighter), make_brighter)
            _registered_hotkeys.append(hk)
        if darker:
            hk = keyboard.add_hotkey(_hotkey_to_keyboard_combo(darker), make_darker)
            _registered_hotkeys.append(hk)
    except Exception as e:
        pass
        # print('Failed to register hotkeys:', e)

# ensure hotkeys are registered at startup
register_hotkeys()

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
    # Do not raise SystemExit from inside the pystray callback.
    # Schedule the Tk mainloop to quit on the main thread instead.
    try:
        overlay.after(0, overlay.quit)
    except Exception:
        try:
            overlay.after(0, overlay.destroy)
        except Exception:
            pass
    return

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