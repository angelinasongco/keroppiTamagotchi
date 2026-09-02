import tkinter as tk
import time
import math
from datetime import datetime
from zoneinfo import ZoneInfo

# ============================================================
# 128x64 OLED SIMULATOR
# SSD1306-style monochrome display
#
# Controls:
#   Arrow keys = move/select
#   Enter/Space = action
#   M = menu
#   R = reset
#   Esc = quit
#
# This uses a REAL 128x64 pixel canvas internally.
# The canvas is simply enlarged on your computer screen.
# ============================================================

OLED_W = 128
OLED_H = 64
SCALE = 7

BG = "#050505"
PIXEL = "#D8D8D8"

# Pacific Time automatically switches between PST (UTC-8) and PDT (UTC-7).
PACIFIC_TIME = ZoneInfo("America/Los_Angeles")

root = tk.Tk()
root.title("128x64 OLED Simulator")
root.resizable(False, False)
root.configure(bg="#202020")

# -----------------------------
# Virtual OLED framebuffer
# -----------------------------
fb = [[0 for _ in range(OLED_W)] for _ in range(OLED_H)]

def clear():
    for y in range(OLED_H):
        for x in range(OLED_W):
            fb[y][x] = 0

def pixel(x, y, value=1):
    if 0 <= x < OLED_W and 0 <= y < OLED_H:
        fb[y][x] = 1 if value else 0

def rect(x, y, w, h, fill=False):
    if fill:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                pixel(xx, yy)
    else:
        for xx in range(x, x + w):
            pixel(xx, y)
            pixel(xx, y + h - 1)
        for yy in range(y, y + h):
            pixel(x, yy)
            pixel(x + w - 1, yy)

def line(x0, y0, x1, y1):
    # Bresenham line algorithm
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    err = dx + dy

    while True:
        pixel(x0, y0)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy

# -----------------------------
# Tiny 5x7 font
# -----------------------------
FONT = {
    "A":["01110","10001","10001","11111","10001","10001","10001"],
    "B":["11110","10001","10001","11110","10001","10001","11110"],
    "C":["01111","10000","10000","10000","10000","10000","01111"],
    "D":["11110","10001","10001","10001","10001","10001","11110"],
    "E":["11111","10000","10000","11110","10000","10000","11111"],
    "F":["11111","10000","10000","11110","10000","10000","10000"],
    "G":["01111","10000","10000","10111","10001","10001","01111"],
    "H":["10001","10001","10001","11111","10001","10001","10001"],
    "I":["11111","00100","00100","00100","00100","00100","11111"],
    "J":["00111","00010","00010","00010","10010","10010","01100"],
    "K":["10001","10010","10100","11000","10100","10010","10001"],
    "L":["10000","10000","10000","10000","10000","10000","11111"],
    "M":["10001","11011","10101","10101","10001","10001","10001"],
    "N":["10001","11001","10101","10011","10001","10001","10001"],
    "O":["01110","10001","10001","10001","10001","10001","01110"],
    "P":["11110","10001","10001","11110","10000","10000","10000"],
    "Q":["01110","10001","10001","10001","10101","10010","01101"],
    "R":["11110","10001","10001","11110","10100","10010","10001"],
    "S":["01111","10000","10000","01110","00001","00001","11110"],
    "T":["11111","00100","00100","00100","00100","00100","00100"],
    "U":["10001","10001","10001","10001","10001","10001","01110"],
    "V":["10001","10001","10001","10001","10001","01010","00100"],
    "W":["10001","10001","10001","10101","10101","11011","10001"],
    "X":["10001","10001","01010","00100","01010","10001","10001"],
    "Y":["10001","10001","01010","00100","00100","00100","00100"],
    "Z":["11111","00001","00010","00100","01000","10000","11111"],
    "0":["01110","10001","10011","10101","11001","10001","01110"],
    "1":["00100","01100","00100","00100","00100","00100","01110"],
    "2":["01110","10001","00001","00010","00100","01000","11111"],
    "3":["11110","00001","00001","01110","00001","00001","11110"],
    "4":["00010","00110","01010","10010","11111","00010","00010"],
    "5":["11111","10000","10000","11110","00001","00001","11110"],
    "6":["01110","10000","10000","11110","10001","10001","01110"],
    "7":["11111","00001","00010","00100","01000","01000","01000"],
    "8":["01110","10001","10001","01110","10001","10001","01110"],
    "9":["01110","10001","10001","01111","00001","00001","01110"],
    ":":["00000","00100","00100","00000","00100","00100","00000"],
    "!":["00100","00100","00100","00100","00100","00000","00100"],
    "?":["01110","10001","00001","00010","00100","00000","00100"],
    "-":["00000","00000","00000","11111","00000","00000","00000"],
    " ":["00000"]*7,
}

def text(x, y, s, scale=1):
    """Draw text onto the 128x64 framebuffer."""
    cursor = x
    for ch in s.upper():
        glyph = FONT.get(ch, FONT["?"])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    for sy in range(scale):
                        for sx in range(scale):
                            pixel(cursor + gx*scale + sx,
                                  y + gy*scale + sy)
        cursor += 6 * scale

# -----------------------------
# Tamagotchi demo state
# -----------------------------
mode = "pet"
frame = 0
selected = 0
hunger = 82
happy = 76
energy = 68
message = ""
message_until = 0

menu_items = ["FOOD", "PLAY", "SLEEP"]

def pet_sprite(cx, cy, anim):
    # Body
    rect(cx-16, cy-15, 32, 28, fill=False)

    # Ears
    line(cx-16, cy-13, cx-22, cy-20)
    line(cx+16, cy-13, cx+22, cy-20)

    # Eyes blink every so often
    blink = (anim % 120) in range(58, 64)
    if blink:
        line(cx-9, cy-3, cx-5, cy-3)
        line(cx+5, cy-3, cx+9, cy-3)
    else:
        rect(cx-9, cy-6, 4, 5, fill=True)
        rect(cx+5, cy-6, 4, 5, fill=True)

    # Nose/mouth
    pixel(cx, cy+1)
    line(cx-4, cy+5, cx, cy+7)
    line(cx, cy+7, cx+4, cy+5)

    # Feet animate
    if (anim // 12) % 2 == 0:
        line(cx-10, cy+13, cx-14, cy+18)
        line(cx+10, cy+13, cx+14, cy+18)
    else:
        line(cx-10, cy+13, cx-7, cy+18)
        line(cx+10, cy+13, cx+7, cy+18)

def bar(x, y, w, value):
    rect(x, y, w, 7)
    inner = max(0, min(w-2, int((w-2) * value / 100)))
    for yy in range(y+2, y+5):
        for xx in range(x+1, x+1+inner):
            pixel(xx, yy)

def draw_pet_screen():
    text(2, 1, "HAPPY", 1)

    # Read the current Pacific time every time the OLED is redrawn.
    # Seconds are included so the clock visibly advances in real time.
    current_time = datetime.now(PACIFIC_TIME).strftime("%I:%M")
    text(76, 1, current_time, 1)

    text(2, 11, "H", 1)
    bar(10, 10, 36, hunger)

    text(2, 20, "F", 1)
    bar(10, 19, 36, happy)

    text(2, 29, "E", 1)
    bar(10, 28, 36, energy)

    pet_sprite(80, 38, frame)


    # Tiny battery icon
    rect(108, 55, 16, 7)
    rect(124, 57, 2, 3)
    for x in range(110, 122, 3):
        pixel(x, 57)
        pixel(x, 58)
        pixel(x, 59)

def draw_menu():
    text(4, 2, "MENU", 1)

    for i, item in enumerate(menu_items):
        y = 16 + i * 14
        if i == selected:
            rect(2, y-2, 124, 11, fill=False)
            text(8, y, ">" + item, 1)
        else:
            text(8, y, item, 1)

def draw_message():
    draw_pet_screen()
    rect(9, 22, 110, 20, fill=True)
    # Invert the message by drawing only selected pixels manually.
    # Simple centered message.
    msg = message.upper()
    width = len(msg) * 6
    text(max(12, (128-width)//2), 29, msg, 1)

def draw():
    clear()

    if message and time.time() < message_until:
        draw_message()
    elif message:
        # Message expired
        globals()["message"] = ""
        draw_pet_screen()
    elif mode == "pet":
        draw_pet_screen()
    else:
        draw_menu()

    # Render the 128x64 framebuffer
    canvas.delete("all")
    for y in range(OLED_H):
        for x in range(OLED_W):
            if fb[y][x]:
                canvas.create_rectangle(
                    x*SCALE, y*SCALE,
                    (x+1)*SCALE, (y+1)*SCALE,
                    fill=PIXEL, outline=""
                )

def action():
    global hunger, happy, energy, message, message_until

    if mode == "pet":
        message = "MENU"
        message_until = time.time() + 0.5
        return

    if selected == 0:
        hunger = min(100, hunger + 18)
        energy = max(0, energy - 2)
        message = "YUM!"
    elif selected == 1:
        happy = min(100, happy + 18)
        energy = max(0, energy - 8)
        message = "FUN!"
    elif selected == 2:
        energy = min(100, energy + 25)
        hunger = max(0, hunger - 4)
        message = "Zzz"

    message_until = time.time() + 0.8

def key(event):
    global mode, selected, hunger, happy, energy, message, message_until

    k = event.keysym.lower()

    if k == "escape":
        root.destroy()
        return

    if k == "r":
        hunger, happy, energy = 82, 76, 68
        mode = "pet"
        selected = 0
        message = ""
        return

    if k == "m":
        mode = "menu" if mode == "pet" else "pet"
        return

    if k in ("return", "space"):
        action()
        return

    if mode == "menu":
        if k in ("up", "w"):
            selected = (selected - 1) % len(menu_items)
        elif k in ("down", "s"):
            selected = (selected + 1) % len(menu_items)
        elif k in ("left", "a", "right", "d"):
            mode = "pet"

canvas = tk.Canvas(
    root,
    width=OLED_W*SCALE,
    height=OLED_H*SCALE,
    bg=BG,
    highlightthickness=0
)
canvas.pack(padx=20, pady=(20, 10))

controls = tk.Label(
    root,
    text="M = menu    ↑/↓ = select    Enter/Space = action    R = reset    Esc = quit",
    fg="white",
    bg="#202020",
    font=("Arial", 10)
)
controls.pack(pady=(0, 15))

root.bind("<Key>", key)
root.focus_force()

def tick():
    global frame, hunger, happy, energy

    frame += 1

    # Slowly simulate pet stats changing
    if frame % 180 == 0:
        hunger = max(0, hunger - 1)
        happy = max(0, happy - 1)
        energy = max(0, energy - 1)

    draw()
    root.after(50, tick)  # ~20 FPS

tick()
root.mainloop()
