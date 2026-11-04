"""A pocket-sized Octolamp for the GitHub Universe 2026 badge."""

import json
import os
import sys

from badgeware import State

APP_DIR = "/system/apps/octolamp"
STATE_FILE = "/state/octolamp.json"
os.chdir(APP_DIR)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from octolamp_core import MODES, PALETTES, adjust, clean_settings, geometry, light_rgb

badge.mode(HIRES | VSYNC)
WIDTH, HEIGHT = screen.width, screen.height
SX, SY = WIDTH / 320, HEIGHT / 240
SIZE = int(min(WIDTH * 0.575, HEIGHT * 0.75))
LAMP_X = int(WIDTH * 0.31 - SIZE / 2)
LAMP_Y = int(HEIGHT * 0.15)
LIGHTS_AVAILABLE = hasattr(badge, "caselights")
AUTO_HIDE_MS = 10000
INPUT_ACTIONS = (
    BUTTON_UP, BUTTON_DOWN, BUTTON_LEFT, BUTTON_RIGHT,
    BUTTON_SELECT, BUTTON_BACK, BUTTON_MENU,
)


def lamp_layout(size, x, y):
    ring, rows = geometry(size)
    points = tuple(
        tuple(vec2(x + px, y + py) for px, py in segment)
        for segment in ring
    )
    return size, x, y, points, rows


CONTROL_LAYOUT = lamp_layout(SIZE, LAMP_X, LAMP_Y)
FULL_SIZE = int(min(WIDTH, HEIGHT) - 20 * min(SX, SY))
FULL_LAYOUT = lamp_layout(
    FULL_SIZE, (WIDTH - FULL_SIZE) // 2, (HEIGHT - FULL_SIZE) // 2,
)

BG = (8, 10, 17)
WHITE = (235, 238, 250)
MUTED = (140, 150, 175)
ACCENT = (196, 146, 255)
phase = 0.0
page = "lamp"
option = 0
controls_visible = True
idle_ms = 0
dirty = False
save_wait = -1
notice = ""
notice_wait = 0
storage_error = False
OPTION_NAMES = (
    "Effect", "Color", "Brightness", "Speed", "Power",
    "Case LEDs", "Auto-hide", "Lamp only", "Controls",
)
OPTION_KEYS = (
    "mode", "palette", "brightness", "speed", "power", "case_lights", "auto_hide",
)
VISIBLE_OPTIONS = 6


def notify(message, error=False):
    global notice, notice_wait, storage_error
    notice = message
    notice_wait = 3500
    if error:
        storage_error = True
    print("Octolamp: " + message)


loaded = {}
try:
    if "state" in os.listdir("/") and "octolamp.json" in os.listdir("/state"):
        with open(STATE_FILE, "r") as saved:
            loaded = json.load(saved)
except (OSError, ValueError) as error:
    notify("Could not load settings: " + str(error), True)
if type(loaded) is not dict:
    loaded = {}
    notify("Could not load settings: expected an object", True)
settings, invalid = clean_settings(loaded)
if invalid:
    notify("Reset invalid settings: " + ", ".join(invalid), True)
if settings["case_lights"] and not LIGHTS_AVAILABLE:
    notify("Case LEDs unavailable on this firmware")


def edited():
    global dirty, save_wait
    dirty = True
    save_wait = 800


def save_settings():
    global dirty, save_wait, storage_error
    save_wait = -1
    try:
        State.save("octolamp", settings)
        # Some firmware State helpers swallow write errors; verify persistence.
        with open(STATE_FILE, "r") as saved:
            if json.load(saved) != settings:
                raise OSError("saved settings do not match")
    except (OSError, ValueError, TypeError) as error:
        notify("Save failed: " + str(error), True)
        return
    dirty = False
    storage_error = False


def pen(rgb, strength=1):
    screen.pen = color.rgb(*(int(c * strength) for c in rgb))


def box(x, y, width, height, rgb):
    pen(rgb)
    screen.rectangle(int(x * SX), int(y * SY), int(width * SX), int(height * SY))


def text(label, x, y, rgb=WHITE, title=False):
    screen.font = font.sins if title else font.smart
    pen(rgb)
    screen.text(label, int(x * SX), int(y * SY))


def meter(x, y, width, fraction, rgb=ACCENT):
    box(x, y, width, 3, (34, 39, 54))
    if fraction > 0:
        box(x, y, max(1, width * fraction), 3, rgb)


def draw_lamp(layout=CONTROL_LAYOUT):
    size, x, y, ring_points, cat_rows = layout
    rgb = light_rgb(settings, phase, 0.25)
    center = vec2(x + size / 2, y + size / 2)
    if settings["power"]:
        for padding in range(9, 0, -2):
            glow = tuple(
                min(255, BG[i] + int(rgb[i] * (10 - padding) * 0.012))
                for i in range(3)
            )
            pen(glow)
            screen.circle(center, size / 2 + padding)
    pen((34, 37, 48))
    screen.circle(center, size / 2)
    pen((17, 19, 28))
    screen.circle(center, size / 2 - 2)
    for index, points in enumerate(ring_points):
        rgb = light_rgb(settings, phase, index / len(ring_points))
        if settings["power"]:
            glow = int(max(rgb) * 0.1)
            rgb = tuple(min(255, channel + glow) for channel in rgb)
        else:
            rgb = (31, 33, 44)
        pen(rgb)
        screen.triangle(points[0], points[1], points[2])
        screen.triangle(points[0], points[2], points[3])
    for row, left, width in cat_rows:
        rgb = light_rgb(settings, phase, row / size)
        if settings["power"]:
            glow = int(max(rgb) * (0.08 + 0.12 * row / size))
            rgb = tuple(min(255, channel + glow) for channel in rgb)
        else:
            rgb = (31, 33, 44)
        pen(rgb, 0.92)
        screen.rectangle(x + left, y + row, width, 1)
        if settings["power"] and width > 4:
            pen(rgb)
            screen.rectangle(x + left, y + row, 1, 1)


def color_label():
    mode = settings["mode"]
    if mode == 2:
        return "Spectrum"
    if mode >= 4:
        return ("Candlelight", "Green", "Red", "Gold")[mode - 4]
    return PALETTES[settings["palette"]][0]


def draw_main():
    text("OCTOLAMP", 10, 8, title=True)
    text("U26 / LOCAL LIGHT", 183, 11, MUTED)
    box(10, 29, 300, 1, (37, 40, 55))
    draw_lamp()
    text("EFFECT", 202, 44, MUTED)
    text(MODES[settings["mode"]].upper(), 202, 59, title=True)
    text("%02d / %02d" % (settings["mode"] + 1, len(MODES)), 202, 78, ACCENT)
    text("COLOR", 202, 100, MUTED)
    text(color_label(), 202, 113)
    text("BRIGHTNESS", 202, 138, MUTED)
    text(str(settings["brightness"]) + "%", 202, 151)
    meter(202, 168, 102, settings["brightness"] / 100)
    is_demo = settings["mode"] >= 5
    status = "OFF" if not settings["power"] else ("OFFLINE DEMO" if is_demo else "LIGHT ON")
    text(status, 202, 188, (255, 205, 100) if is_demo else ACCENT)
    box(10, 215, 300, 1, (37, 40, 55))
    text("< > EFFECT   UP/DN BRIGHTNESS", 10, 216, MUTED)
    text("SEL ON/OFF/LAMP   MENU OPTIONS", 10, 227, MUTED)


def option_value(index):
    if index >= len(OPTION_KEYS):
        return "SELECT to view"
    key = OPTION_KEYS[index]
    if key == "mode":
        return MODES[settings[key]]
    if key == "palette":
        return PALETTES[settings["palette"]][0]
    if key == "brightness":
        return str(settings[key]) + "%"
    if key == "speed":
        return str(settings["speed"]) + " / 5"
    if key == "case_lights" and not LIGHTS_AVAILABLE:
        return "Unavailable"
    return "On" if settings[key] else "Off"


def draw_options():
    text("LAMP OPTIONS", 12, 12, title=True)
    text("%d/%d" % (option + 1, len(OPTION_NAMES)), 274, 12, MUTED)
    text("UP/DN choose   < > change", 12, 34, MUTED)
    start = min(max(0, option - VISIBLE_OPTIONS + 1), len(OPTION_NAMES) - VISIBLE_OPTIONS)
    for index in range(start, start + VISIBLE_OPTIONS):
        y = 56 + (index - start) * 25
        if index == option:
            box(8, y - 4, 304, 23, (32, 26, 51))
            box(8, y - 4, 3, 23, ACCENT)
        text(OPTION_NAMES[index], 20, y, WHITE if index == option else MUTED)
        text(option_value(index), 168, y, ACCENT)
    text("Color: Solid / Breathe / Chase", 12, 207, MUTED)
    text("MENU or BACK returns to lamp", 12, 224, MUTED)


def draw_help():
    text("POCKET OCTOLAMP", 12, 12, title=True)
    lines = (
        "< / >     Previous / next effect",
        "UP / DOWN  Brightness (10-100%)",
        "SELECT    On / off / lamp-only",
        "BACK      Next color",
        "MENU      All settings / lamp-only view",
        "HOME      Return to badge menu",
        "",
        "Auto-hide: 10s without input.",
        "Any button restores the controls.",
        "Build / star effects are offline demos.",
        "Case LEDs are white, not RGB.",
        "Settings save after you stop editing.",
        "Inspired by martinwoodward/octolamp",
    )
    for index, line in enumerate(lines):
        text(line, 12, 43 + index * 13, MUTED)
    text("SELECT / BACK: options   MENU: lamp", 12, 224, ACCENT)


def change_option(delta):
    if option >= len(OPTION_KEYS):
        return
    key = OPTION_KEYS[option]
    if key in ("mode", "palette", "brightness", "speed"):
        if adjust(settings, key, delta * (10 if key == "brightness" else 1)):
            edited()
    elif key == "case_lights" and not LIGHTS_AVAILABLE:
        notify("Case LEDs unavailable on this firmware")
    else:
        settings[key] = not settings[key]
        edited()


def handle_input():
    global page, option, controls_visible
    if page == "help":
        if badge.pressed(BUTTON_MENU):
            page = "lamp"
        elif badge.pressed(BUTTON_BACK) or badge.pressed(BUTTON_SELECT):
            page = "options"
        return
    if page == "options":
        if badge.pressed(BUTTON_BACK) or badge.pressed(BUTTON_MENU):
            page = "lamp"
            return
        if badge.pressed(BUTTON_UP):
            option = (option - 1) % len(OPTION_NAMES)
        if badge.pressed(BUTTON_DOWN):
            option = (option + 1) % len(OPTION_NAMES)
        if badge.pressed(BUTTON_LEFT):
            change_option(-1)
        if badge.pressed(BUTTON_RIGHT):
            change_option(1)
        if badge.pressed(BUTTON_SELECT):
            if OPTION_NAMES[option] == "Controls":
                page = "help"
            elif OPTION_NAMES[option] == "Lamp only":
                page = "lamp"
                controls_visible = False
            else:
                change_option(1)
        return
    if badge.pressed(BUTTON_MENU):
        page = "options"
        return
    for action, key, delta in (
        (BUTTON_LEFT, "mode", -1), (BUTTON_RIGHT, "mode", 1),
        (BUTTON_UP, "brightness", 10), (BUTTON_DOWN, "brightness", -10),
        (BUTTON_BACK, "palette", 1),
    ):
        if badge.pressed(action) and adjust(settings, key, delta):
            edited()
    if badge.pressed(BUTTON_SELECT):
        settings["power"] = not settings["power"]
        if settings["power"]:
            controls_visible = False
        edited()


def update_controls(dt):
    global controls_visible, idle_ms
    pressed = any(badge.pressed(action) for action in INPUT_ACTIONS)
    if not controls_visible:
        if pressed or storage_error or notice_wait > 0:
            controls_visible = True
            idle_ms = 0
        return
    if pressed:
        idle_ms = 0
        handle_input()
    elif page == "lamp" and settings["auto_hide"]:
        idle_ms += dt
        if idle_ms >= AUTO_HIDE_MS:
            controls_visible = False
    if page != "lamp" or storage_error or notice_wait > 0:
        controls_visible = True
        idle_ms = 0


def update():
    global phase, save_wait, notice_wait
    dt = max(0, badge.ticks_delta)
    phase = (phase + dt / 1000 * settings["speed"] / 2) % 120
    notice_wait = max(0, notice_wait - dt)
    if dirty and save_wait >= 0:
        save_wait -= dt
        if save_wait <= 0:
            save_settings()
    update_controls(dt)
    if LIGHTS_AVAILABLE:
        level = 0
        if settings["case_lights"]:
            level = max(light_rgb(settings, phase, 0.25)) / 255 * 0.25
        badge.caselights(level)
    pen(BG)
    screen.rectangle(screen.clip)
    if not controls_visible:
        draw_lamp(FULL_LAYOUT)
    elif page == "lamp":
        draw_main()
    elif page == "options":
        draw_options()
    else:
        draw_help()
    if notice_wait > 0 or storage_error:
        box(8, 200, 304, 14, (65, 23, 35) if storage_error else (32, 26, 51))
        message = "SETTINGS ERROR - see USB console" if storage_error else notice
        text(message, 12, 202, WHITE)


def on_exit():
    if LIGHTS_AVAILABLE:
        badge.caselights(0)
    if dirty:
        save_settings()


run(update)
