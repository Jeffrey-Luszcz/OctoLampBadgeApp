# Octolamp

Octolamp brings a glowing GitHub lamp, animated lighting effects, and offline GitHub event demos to your badge.

## Usage

Open **Octolamp** from the badge menu for a continuous glowing ring and cat
silhouette inspired by Martin Woodward's physical Octolamp.

| Control | Action |
| --- | --- |
| LEFT / RIGHT | Previous / next effect |
| UP / DOWN | Brightness, from 10% to 100% |
| SELECT / Enter | Cycle controls on, lamp off, and lamp-only on |
| BACK | Next color palette |
| MENU | Open options |
| HOME | Return to the badge launcher |

From the main display, repeated SELECT/Enter presses cycle **controls on >
lamp off > lamp-only on > controls on**. The Power row in options remains
a simple on/off toggle.

In options, UP/DOWN selects a row, LEFT/RIGHT changes its value, SELECT
changes it or opens a view, and BACK/MENU returns to the lamp. The list
scrolls and includes every setting: effect, color, brightness, speed,
power, case LEDs, and Auto-hide, followed by Lamp only and Controls.

### Lamp-only view

After **10 seconds without input**, the labels and controls disappear and a
larger, centered lamp fills the display. Its animation and case lighting
continue with the settings you chose. Press any app button to bring back
the controls; that first press **does not change settings or toggle power**.
HOME always returns to the badge launcher.

Choose **MENU > Lamp only > SELECT** to hide the controls immediately.
Choose **MENU > Auto-hide > Off** to keep controls visible until you hide
them manually. Options and help never disappear while you are choosing
settings. Storage errors reveal the controls so warnings cannot be hidden.

### Effects and settings

Solid, Breathe, Rainbow, Chase, Candle, Build OK, Build fail, and New star.
The last three are **offline visual demos**, not live GitHub notifications.
Color palettes apply to Solid, Breathe, and Chase; the other effects use
their own colors. Speed (1-5) controls animation, not Solid.

The default color is magenta, matching the original lamp's project photo.
Brightness changes the rendered lamp, not the LCD backlight. Optional case
lighting mirrors the effect's intensity using the badge's **white** LEDs,
capped at 25% drive. It defaults off and is cleared when leaving the app.
Firmware without `badge.caselights` displays "Unavailable" in options.

Power, effect, palette, brightness, speed, case-light preference, and Auto-hide save
after 800 ms without edits and on exit to `/state/octolamp.json`. Invalid
values reset to defaults with a visible warning; load/save failures are
reported on screen and in the USB console. A failed save is retried after
another edit or on exit, rather than blocking the frame loop with retries.

No Wi-Fi, credentials, extra hardware, or third-party MicroPython packages
are required. The app uses the Universe 2026 runtime, not the 2025 API.

## Install

1. Connect the badge over USB-C and open **Mass Storage**, or quickly
   double-tap RESET to show the **BADGER** drive.
2. Copy this entire `octolamp` folder into `BADGER/apps/` (or
   `BADGER/system/apps/`, if that is where the installed apps live).
   Do not copy to an `RP2350` firmware drive.
3. Eject BADGER, let the badge restart, and open **Octolamp**.

The app includes a 48x48 menu icon. Stock event firmware may need the
hyb26-skill menu-icon patch before custom icons appear; the app itself does
not require the patch.

With hyb26-skill installed, run these from the project root:

```sh
scripts="$HOME/.copilot/skills/hyb26-skill/scripts"
python3 "$scripts/validate_app.py" badge/apps/octolamp
python3 "$scripts/deploy_app.py" badge/apps/octolamp
# After reviewing the preview and connecting BADGER in USB Disk Mode:
python3 "$scripts/deploy_app.py" badge/apps/octolamp --write
python3 "$scripts/badge_serial.py" eject
```

## Development and physical checks

```sh
python3 -m unittest discover -s tests -v
python3 tools/render_preview.py --output preview.png
```

Preview rendering requires Pillow on the computer only. It also regenerates
`icon.png` from the same geometry used by the app. A desktop render or mocked
runtime test does not verify the physical badge.

On the badge, check all eight effects, brightness limits, power, palettes,
options, speed, help, and both orientations. Enable case lighting, then turn
the lamp off and leave with HOME to verify LED cleanup. Reopen/reset to
verify saved settings. Test missing/corrupt state and a failed save via the
USB console; verify the visible error and continued responsive controls.
Check the 10-second idle transition, manual Lamp only action, Auto-hide
toggle, and that each first wake-up button only restores controls.
Check real frame rate, text legibility, repeated launches, and memory use.

## Inspiration and attribution

Original project: https://github.com/martinwoodward/octolamp by Martin Woodward.
Its README and reference photos inspired the black casing, luminous diffuser,
magenta color, WLED-style effects, and build/star automation demos. This app
has independently written code and a simplified, programmatically drawn
outline; it does not redistribute the project's photos, models, or firmware.
The original project is licensed CC BY-NC 4.0. GitHub owns the Invertocat
trademark; this is an unofficial badge adaptation, not WLED or Home Assistant.
