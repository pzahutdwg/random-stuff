from tkinter import *

root = Tk()
root.geometry("250x100")

# Center the window on the screen
root.update_idletasks()
w = root.winfo_width()
h = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (w // 2)
y = (root.winfo_screenheight() // 2) - (h // 2)
root.geometry(f"{w}x{h}+{x}+{y}")

root.configure(bg="#FF00C8")

colors = ["#FF00C8", "#FFC400", "#C7FF44", "#98FFE9"]
currentColor = colors[0]

tick = 0
time = 3  # in seconds

countdownLabel = Label(root, text=f"Epic disco party in {time}", font=("Helvetica", 16), bg=currentColor)
countdownLabel.pack(pady=20)

def main():
    global tick, currentColor

    tick += 1
    currentColor = colors[tick % len(colors)]
    root.configure(bg=currentColor)

    if tick % 20 == 0:  # 20 ticks * 50ms = 1 second
        global time
        if time > 0:
            time -= 1
            countdownLabel.config(text=f"Epic disco party in {time}")
    
    if time == 0:
        countdownLabel.config(text="DISCO TIME!!!")

    countdownLabel.config(bg=currentColor)

    root.after(50, main)  # Call main again after 50ms

def disco():
    pass

main()
root.mainloop()