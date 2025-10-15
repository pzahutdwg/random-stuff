from tkinter import *
import screen_brightness_control as sbc
import ctypes
import random
import subprocess
import keyboard
from reqs.keys import keys
# from playsound import playsound

string = list("DISCO TIME!!! ")
discoIterator = 0

def remap(e):
    global discoIterator
    
    if e.event_type == 'down':
        print(discoIterator)
        keyboard.write(string[discoIterator % len(string)])
        discoIterator += 1

keyboard.hook(lambda e: remap(e), True)

root = Tk()
root.geometry("250x100")

colorOverlay = Tk()
colorOverlay.attributes("-topmost", True)
colorOverlay.geometry(f"{colorOverlay.winfo_screenwidth()}x{colorOverlay.winfo_screenheight()}+0+0")
colorOverlay.configure(bg="#FF00C8")
colorOverlay.attributes("-alpha", 0.3)
colorOverlay.overrideredirect(True)
colorOverlay.lift()
colorOverlay.attributes("-disabled", True)

colorOverlay.update_idletasks()
hwnd = ctypes.windll.user32.GetParent(colorOverlay.winfo_id())
style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20)

root.update_idletasks()
w = root.winfo_width()
h = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (w // 2)
y = (root.winfo_screenheight() // 2) - (h // 2)
root.geometry(f"{w}x{h}+{x}+{y}")

root.overrideredirect(True)
root.configure(bg="#FF00C8")
root.attributes("-topmost", True)

colors = ["#FF00C8", "#FFC400", "#C7FF44", "#98FFE9", "#FFA500", "#B609B6"]
currentColor = colors[0]

tick = 0
time = 60  # in seconds
discoMode = False
lvl = 0

countdownLabel = Label(root, text=f"Epic disco party in {time}", font=("Helvetica", 16), bg=currentColor)
countdownLabel.pack(pady=20)

subprocess.Popen(['reqs/nircmd', 'speak', 'text', f'epic disco party in {time}'])

def main():
    global tick, currentColor, discoMode, time
    tick += 1
    
    if tick % 10 == 0:
        subprocess.Popen(["reqs/nircmd.exe", "setsysvolume", "65535"])
        subprocess.Popen(["reqs/nircmd.exe", "mutesysvolume", "0"])

    # Change background color
    currentColor = colors[tick % len(colors)]
    root.configure(bg=currentColor)

    if tick % 20 == 0:  # 20 ticks * 50ms = 1 second
        time -= 1

        if time > 0:
            subprocess.Popen(['reqs/nircmd', 'speak', 'text', f'{time}'])
            countdownLabel.config(text=f"Epic disco party in {time}")
    
    if time <= 0:
        countdownLabel.config(text="DISCO TIME!!!")

        if not discoMode:
            sbc.set_brightness(sbc.get_brightness()[0] + 5)

            if time < -2 and sbc.get_brightness()[0] >= 100:
                discoMode = True
                countdownLabel.config(text="DISCO TIME!!!")

    if discoMode:
        disco()
    

    countdownLabel.config(bg=currentColor)

    root.after(50, main)  # Call main again after 50ms

musicPlayed = False

def disco():
    global lvl, musicPlayed
    lvl += 0.0075
    print(time)
    if tick % 20 == 0:
        sbc.set_brightness(100)
    colorOverlay.configure(bg=currentColor)
    alpha = random.random() * lvl + lvl
    # alpha = random.random() * 0
    colorOverlay.attributes("-alpha", alpha)

    if time <= -3 and musicPlayed == False:
        musicPlayed = True
        print('Yes!')
        subprocess.Popen(['reqs\\nircmd', 'mediaplay', '1000000000', 'reqs\\googoog.mp3'])

main()
root.mainloop()