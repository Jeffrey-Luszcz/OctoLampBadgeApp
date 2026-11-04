"""Hardware-independent lighting and geometry for the badge Octolamp."""

import math


MODES = (
    "Solid",
    "Breathe",
    "Rainbow",
    "Chase",
    "Candle",
    "Build OK",
    "Build fail",
    "New star",
)
PALETTES = (
    ("Magenta", (255, 35, 175)),
    ("Cyan", (25, 205, 255)),
    ("Violet", (145, 75, 255)),
    ("Amber", (255, 125, 25)),
    ("Mint", (40, 255, 150)),
    ("Warm white", (255, 218, 165)),
)
DEFAULTS = {
    "mode": 0,
    "palette": 0,
    "brightness": 80,
    "speed": 2,
    "power": True,
    "case_lights": False,
    "auto_hide": True,
}
RANGES = {
    "mode": (0, len(MODES) - 1),
    "palette": (0, len(PALETTES) - 1),
    "brightness": (10, 100),
    "speed": (1, 5),
}

# An original outline on a 100x100 canvas, joining the circular diffuser below.
CAT = (
    (28, 29), (27, 25), (27, 20), (30, 20), (34, 22),
    (39, 25), (44, 24), (50, 23.5), (56, 24), (61, 25),
    (66, 22), (70, 20), (73, 20), (73, 25), (72, 29),
    (75, 34), (77, 40), (77, 45), (76, 50), (74, 54),
    (70, 57), (65, 59), (58, 60), (60, 62), (61.5, 65),
    (62, 70), (62, 88), (63, 92), (37, 92), (38, 88),
    (38, 77), (34, 78), (30, 77.5), (26, 76), (23, 73),
    (20, 68), (17, 66), (16, 64), (17, 62.5), (20, 63),
    (23, 65), (26, 68.5), (29, 71), (32, 72), (35, 72),
    (38, 70.5), (39, 66), (40, 63), (43, 60), (35, 59),
    (30, 57), (26, 54), (24, 50), (23, 45), (23, 40),
    (25, 34),
)


def clean_settings(raw):
    settings = DEFAULTS.copy()
    invalid = []
    for key, default in DEFAULTS.items():
        if key not in raw:
            continue
        value = raw[key]
        valid = type(value) is type(default)
        if key in RANGES and valid:
            low, high = RANGES[key]
            valid = low <= value <= high
        if valid:
            settings[key] = value
        else:
            invalid.append(key)
    return settings, invalid


def adjust(settings, key, delta):
    low, high = RANGES[key]
    value = settings[key] + delta
    if key in ("mode", "palette"):
        value = low + (value - low) % (high - low + 1)
    else:
        value = min(high, max(low, value))
    changed = value != settings[key]
    settings[key] = value
    return changed


def wheel(hue):
    sector = (hue % 1.0) * 6
    index = int(sector)
    rise = int(255 * (sector - index))
    fall = 255 - rise
    return (
        (255, rise, 0), (fall, 255, 0), (0, 255, rise),
        (0, fall, 255), (rise, 0, 255), (255, 0, fall),
    )[index]


def light_rgb(settings, phase, position):
    if not settings["power"]:
        return (0, 0, 0)
    mode = settings["mode"]
    rgb = PALETTES[settings["palette"]][1]
    strength = 1.0
    if mode == 1:
        strength = 0.2 + 0.8 * (0.5 - 0.5 * math.cos(phase * math.pi))
    elif mode == 2:
        rgb = wheel(position + phase * 0.1)
    elif mode == 3:
        distance = (phase * 0.25 - position) % 1.0
        strength = 0.1 + 0.9 * max(0, 1 - distance / 0.3) ** 2
    elif mode == 4:
        rgb = (255, 119, 26)
        strength = (
            0.76 + 0.12 * math.sin(phase * 7.3)
            + 0.07 * math.sin(phase * 17.1 + position * 2)
            + 0.04 * math.sin(phase * 31.7)
        )
    elif mode == 5:
        rgb = (48, 235, 115)
        strength = 0.8 + 0.2 * math.sin(phase * math.pi / 2) ** 2
    elif mode == 6:
        rgb = (255, 50, 65)
        beat = phase % 2.4
        strength = 1.0 if beat < 0.22 or 0.44 <= beat < 0.66 else 0.25
    elif mode == 7:
        rgb = (255, 205, 65)
        strength = 0.35 + 0.65 * max(
            0, math.cos(position * math.pi * 6 - phase * math.pi / 2)
        ) ** 8
    strength *= settings["brightness"] / 100
    return tuple(min(255, max(0, int(channel * strength))) for channel in rgb)


def geometry(size):
    """Precompute the continuous ring mesh and scan-converted cat once."""
    center = size / 2
    outer, inner = size * 0.48, size * 0.415
    ring = []
    for index in range(72):
        a = index * 2 * math.pi / 72 - math.pi / 2
        b = (index + 1) * 2 * math.pi / 72 - math.pi / 2
        points = []
        for angle, radius in ((a, outer), (b, outer), (b, inner), (a, inner)):
            points.append((
                center + math.cos(angle) * radius,
                center + math.sin(angle) * radius,
            ))
        ring.append(tuple(points))

    polygon = [(x * size / 100, y * size / 100) for x, y in CAT]
    rows = []
    for y in range(size):
        intersections = []
        previous = polygon[-1]
        for current in polygon:
            x1, y1 = previous
            x2, y2 = current
            if min(y1, y2) <= y + 0.5 < max(y1, y2):
                intersections.append(x1 + (y + 0.5 - y1) * (x2 - x1) / (y2 - y1))
            previous = current
        intersections.sort()
        for i in range(0, len(intersections), 2):
            left = int(math.ceil(intersections[i]))
            right = int(math.ceil(intersections[i + 1]))
            if right > left:
                rows.append((y, left, right - left))
    return ring, rows
