import tkinter as tk
import time
import math
import random
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
#   G = show/hide pixel grid
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
GRID_COLOR = "#303030"
SHOW_GRID = True

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

def circle(cx, cy, radius, fill=False):
    """Draw a circle centered at (cx, cy)."""
    for y in range(-radius, radius + 1):
        for x in range(-radius, radius + 1):
            distance = x*x + y*y

            if fill:
                if distance <= radius*radius:
                    pixel(cx + x, cy + y)
            else:
                if (radius - 1)**2 <= distance <= radius**2:
                    pixel(cx + x, cy + y)

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
    # Kannada letter SHORT A (಄), simplified for the 5x7 OLED grid.
    "಄":["01110","10001","00111","01001","10111","10001","01110"],
    # Four-point sparkle/star (✦), simplified for the 5x7 OLED grid.
    "✦":["00100","10101","01110","11111","01110","10101","00100"],
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

# -----------------------------
# Frog runner game state
# -----------------------------
GROUND_Y = 55
frog_x = 18
frog_y = 47.0
frog_velocity = 0.0
frog_on_ground = True
runner_obstacles = []
runner_spawn_timer = 45
runner_score = 0
runner_game_over = False

def pet_sprite(cx, cy, anim):
    """Draw a smaller Keroppi-style frog."""

    # Gentle bouncing animation
    cy -= (anim // 12) % 2

    # Smaller connected eyes
    circle(cx - 6, cy - 8, 7, fill=False)
    circle(cx + 6,cy - 8, 7, fill=False)

    # Blink periodically
    blink = (anim % 120) in range(58, 64)

    if blink:
        line(cx - 10, cy - 8, cx, cy - 8)
        line(cx, cy - 8, cx + 10, cy - 8)
    else:
        # Smaller pupils
        rect(cx - 5, cy - 8, 3, 3, fill=True) #left eye
        rect(cx + 3, cy - 8, 3, 3, fill=True) #right eye


    # Smaller face outline
    line(cx - 11, cy - 4, cx - 14, cy - 1)
    line(cx - 14, cy - 1, cx - 14, cy + 4)
    line(cx - 14, cy + 4, cx - 11, cy + 7)

    line(cx + 11, cy - 4, cx + 14, cy - 1)
    line(cx + 14, cy - 1, cx + 14, cy + 4)
    line(cx + 14, cy + 4, cx + 11, cy + 7)

    # Bottom of face
    line(cx - 11, cy + 7, cx - 7, cy + 9)
    line(cx - 7, cy + 9, cx, cy + 10)
    line(cx, cy + 10, cx + 7, cy + 9)
    line(cx + 7, cy + 9, cx + 11, cy + 7)

    # Smaller cheeks
    circle(cx - 10, cy + 1, 2, fill=True)
    circle(cx + 10, cy + 1, 2, fill=True)

    # Smaller smile
    line(cx - 6, cy + 3, cx - 4, cy + 5)
    line(cx - 4, cy + 5, cx - 2, cy + 5)
    line(cx - 2, cy + 5, cx, cy + 7)

    line(cx, cy + 7, cx + 2, cy + 5)
    line(cx + 2, cy + 5, cx + 4, cy + 5)
    line(cx + 4, cy + 5, cx + 6, cy + 3)

# def pet_sprite(cx, cy, anim):
#     """Draw a tiny monochrome Keroppi-style frog pet."""
#     # Move the character up one pixel every few frames for a gentle bounce.
#     cy -= (anim // 12) % 2

#     # Large connected frog eyes. The OLED is monochrome, so white areas in
#     # the reference image are represented by empty pixels inside the outlines.
#     circle(cx - 9, cy - 13, 10, fill=False)
#     circle(cx + 9, cy - 13, 10, fill=False)

#     # Blink periodically; otherwise draw the square pupils from the reference.
#     blink = (anim % 120) in range(58, 64)
#     if blink:
#         #left eye
#         line(cx-17, cy-12, cx, cy-12)
#         # right eye
#         line(cx, cy-12, cx+17, cy-12)
#     else:
#         circle(cx-6, cy-13, 3, fill=True)
#         circle(cx+6, cy-13, 3, fill=True)

#     # Wide frog face and round cheeks.
#     # pixel(cx-18, cy)
#     line(cx-17, cy-6, cx-21, cy-1)
#     line(cx-21, cy, cx-21, cy+5)
#     line(cx+17, cy-6, cx+21, cy-1)
#     line(cx+21, cy, cx+21, cy+5)
#     line(cx-21, cy+5, cx-17, cy+10)
#     line(cx+21, cy+5, cx+17, cy+10)
#     line(cx+16, cy+11, cx+13, cy+11) # right side detail
#     line(cx-16, cy+11, cx-13, cy+11) # left side detail
#     line(cx+13, cy+12, cx+10, cy+12) # right side detail continuation
#     line(cx-13, cy+12, cx-10, cy+12) # left side detail continuation
#     line(cx+10, cy+13, cx, cy+14) # right side detail continuation
#     line(cx-10, cy+13, cx, cy+14) # left side detail continuation


#     circle(cx-15, cy+2, 3, fill=True) # left cheek
#     circle(cx+15, cy+2, 3, fill=True) # right cheek
#     # rect(cx-19, cy, 7, 6, fill=False)
#     # rect(cx+12, cy, 7, 6, fill=False)

#     # Keroppi's curved smile.
#     line(cx-10, cy+6, cx-7, cy+9)
#     line(cx-7, cy+9, cx-3, cy+9)
#     line(cx-3, cy+9, cx, cy+11)
#     line(cx, cy+11, cx+3, cy+9)
#     line(cx+3, cy+9, cx+7, cy+9)
#     line(cx+7, cy+9, cx+10, cy+6)

#     # # Short arms beside the striped shirt.
#     # line(cx-18, cy+10, cx-23, cy+15)
#     # line(cx-23, cy+15, cx-19, cy+18)
#     # line(cx+18, cy+10, cx+23, cy+15)
#     # line(cx+23, cy+15, cx+19, cy+18)

#     # # Shirt outline and three dark horizontal stripes.
#     # rect(cx-16, cy+11, 32, 17, fill=False)
#     # rect(cx-15, cy+13, 30, 3, fill=True)
#     # rect(cx-15, cy+19, 30, 3, fill=True)
#     # rect(cx-15, cy+25, 30, 2, fill=True)

#     # Feet alternate slightly to preserve the original walking animation.
#     # if (anim // 12) % 2 == 0:
#     #     rect(cx-15, cy+28, 12, 4, fill=False)
#     #     rect(cx+5, cy+28, 12, 4, fill=False)
#     # else:
#     #     rect(cx-13, cy+28, 12, 4, fill=False)

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
    current_time = datetime.now(PACIFIC_TIME).strftime("%I:%M:%S")
    text(76, 1, current_time, 1)

    text(2, 11, "H", 1)
    bar(10, 10, 36, hunger)

    text(2, 20, "F", 1)
    bar(10, 19, 36, happy)

    text(2, 29, "E", 1)
    bar(10, 28, 36, energy)

    # Center the 48x53 frog sprite in the open area on the right.
    pet_sprite(80, 31, frame)


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

def reset_runner():
    """Return the frog runner to its starting state."""
    global frog_y, frog_velocity, frog_on_ground
    global runner_obstacles, runner_spawn_timer
    global runner_score, runner_game_over

    frog_y = 47.0
    frog_velocity = 2.0
    frog_on_ground = True
    runner_obstacles = []
    runner_spawn_timer = 45
    runner_score = 0
    runner_game_over = False

def jump_runner():
    """Start a jump only when the frog is standing on the ground."""
    global frog_velocity, frog_on_ground

    if frog_on_ground and not runner_game_over:
        frog_velocity = -4.7
        frog_on_ground = False

def boxes_touch(x1, y1, w1, h1, x2, y2, w2, h2):
    """Return True when two rectangular hitboxes overlap."""
    return (
        x1 < x2 + w2 and
        x1 + w1 > x2 and
        y1 < y2 + h2 and
        y1 + h1 > y2
    )

def draw_runner_frog(x, y):
    """Draw the small playable frog at integer OLED coordinates."""
    x = int(x)
    y = int(y)

    # Body, two raised eyes, pupils, and two feet.
    rect(x + 1, y + 2, 8, 6, fill=False)
    rect(x + 1, y, 3, 3, fill=False)
    rect(x + 6, y, 3, 3, fill=False)
    pixel(x + 2, y + 1)
    pixel(x + 7, y + 1)
    line(x, y + 7, x + 3, y + 7)
    line(x + 7, y + 7, x + 10, y + 7)

def draw_runner():
    """Draw one frame of the frog obstacle-jumping game."""
    text(2, 1, "FROG RUN", 1)
    text(98, 1, str(runner_score), 1)

    # Ground and small scrolling marks make movement easier to see.
    line(0, GROUND_Y, OLED_W - 1, GROUND_Y)
    ground_shift = (frame // 2) % 12
    for x in range(-ground_shift, OLED_W, 12):
        line(x, GROUND_Y + 4, x + 4, GROUND_Y + 4)

    draw_runner_frog(frog_x, frog_y)

    for obstacle in runner_obstacles:
        ox = int(obstacle["x"])
        oy = GROUND_Y - obstacle["h"]
        rect(ox, oy, obstacle["w"], obstacle["h"], fill=True)
        # One-pixel branch makes each obstacle resemble a tiny plant.
        if obstacle["h"] >= 8:
            line(ox - 2, oy + 3, ox, oy + 3)

    if runner_game_over:
        rect(25, 20, 78, 22, fill=False)
        text(31, 24, "GAME OVER", 1)
        text(34, 33, "R=RETRY", 1)

def update_runner():
    """Apply gravity, move obstacles, score, and detect collisions."""
    global frog_y, frog_velocity, frog_on_ground
    global runner_spawn_timer, runner_score, runner_game_over

    if runner_game_over:
        return

    # Jump physics: negative velocity rises; gravity pulls the frog down.
    frog_velocity += 0.38
    frog_y += frog_velocity

    if frog_y >= 47:
        frog_y = 47.0
        frog_velocity = 0.0
        frog_on_ground = True

    # Increase speed gradually as the score rises.
    speed = min(4.0, 2.0 + runner_score / 250.0)
    for obstacle in runner_obstacles:
        obstacle["x"] -= speed

    runner_obstacles[:] = [
        obstacle for obstacle in runner_obstacles
        if obstacle["x"] + obstacle["w"] >= 0
    ]

    runner_spawn_timer -= 1
    if runner_spawn_timer <= 0:
        height = random.choice([6, 8, 10, 12])
        runner_obstacles.append({"x": 128.0, "w": 5, "h": height})
        runner_spawn_timer = random.randint(38, 65)

    # Use a slightly smaller hitbox than the drawing for fair collisions.
    for obstacle in runner_obstacles:
        if boxes_touch(
            frog_x + 1, int(frog_y) + 1, 8, 7,
            int(obstacle["x"]), GROUND_Y - obstacle["h"],
            obstacle["w"], obstacle["h"]
        ):
            runner_game_over = True
            return

    runner_score += 1

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
    elif mode == "runner":
        draw_runner()
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

    # Draw grid lines last so the boundary of every OLED pixel stays visible,
    # including the boundaries between neighboring filled pixels.
    if SHOW_GRID:
        for x in range(OLED_W + 1):
            canvas.create_line(
                x*SCALE, 0, x*SCALE, OLED_H*SCALE,
                fill=GRID_COLOR
            )
        for y in range(OLED_H + 1):
            canvas.create_line(
                0, y*SCALE, OLED_W*SCALE, y*SCALE,
                fill=GRID_COLOR
            )

def action():
    global mode, hunger, happy, energy, message, message_until

    if mode == "pet":
        message = "MENU"
        message_until = time.time() + 0.5
        return

    if selected == 0:
        hunger = min(100, hunger + 18)
        energy = max(0, energy - 2)
        message = "YUM!"
    elif selected == 1:
        reset_runner()
        mode = "runner"
        message = ""
        return
    elif selected == 2:
        energy = min(100, energy + 25)
        hunger = max(0, hunger - 4)
        message = "Zzz"

    message_until = time.time() + 0.8

def key(event):
    global mode, selected, hunger, happy, energy, message, message_until
    global SHOW_GRID

    k = event.keysym.lower()

    if k == "escape":
        root.destroy()
        return

    if k == "r":
        if mode == "runner":
            reset_runner()
            return
        hunger, happy, energy = 82, 76, 68
        mode = "pet"
        selected = 0
        message = ""
        return

    if k == "m":
        mode = "menu" if mode in ("pet", "runner") else "pet"
        return

    if k == "g":
        SHOW_GRID = not SHOW_GRID
        return

    if mode == "runner" and k in ("return", "space", "up", "w"):
        jump_runner()
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
    text="M = menu    G = grid    ↑/↓ = select    Space = jump/action    R = reset    Esc = quit",
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

    if mode == "runner":
        update_runner()

    draw()
    root.after(50, tick)  # ~20 FPS

tick()
root.mainloop()
