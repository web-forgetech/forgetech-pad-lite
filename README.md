# Forgetech Pad Lite (ESP32-C3 BLE Xbox Controller)

By **Forgetech**, Lahore.

A wireless Bluetooth LE controller on the ESP32-C3-MINI-1 dev board: **A, B, 4 direction buttons + auto-fire (turbo)**.
It emulates an **Xbox Series X Wireless Controller** (XInput, VID `0x045E` / PID `0x0B13`, via ESP32-BLE-Gamepad's
`GamepadMode::XInputSeriesX`), so one device covers:

| Host | How it appears |
|---|---|
| macOS | Xbox Wireless Controller (Game Controller framework, built in since Big Sur) |
| Windows in Parallels | **Virtual Xbox Controller** (pair with the Mac, Parallels 18+ shares it with Windows 10/11) |
| Windows (native Bluetooth) | Xbox Wireless Controller |

| Button | Xbox input |
|---|---|
| A | A (auto-fire: fires by itself while turbo is ON) |
| B | B |
| Direction buttons (Up/Down/Left/Right) | **Left analog stick**, full tilt (diagonals at 70.7 % per axis, opposite directions cancel) |

## Wiring
![Forgetech Pad Lite button pinout](docs/wiring.png)

| Function | GPIO | Board header |
|---|---|---|
| A / B | 5 / 6 | right pin 10 / right 9 |
| D-pad Up / Down / Left / Right | 0 / 1 / 3 / 4 | left 9 / left 10 / left 5 / right 11 |
| Turbo button | 7 | right pin 8 |
| RGB status LED | 8 | onboard WS2812 |

Wire every button between its GPIO and GND (the internal pull-ups are used, no resistors needed).
All inputs are debounced (20 ms).

Pins kept free on purpose: GPIO2, GPIO8, GPIO9 are strapping pins (boot mode), GPIO20/21 are the CH340 serial link.
GPIO10, GPIO18 and GPIO19 are still free for future inputs (e.g. X / Y / Start).

## Auto-fire (turbo)
- Press the turbo button: auto-fire **ON** (LED orange). Press again: **OFF** (LED green).
- Works **only on A**. While ON, A **fires by itself** at **10 shots/second** (50 ms pressed / 50 ms released) — no need to touch A.
- **Press and hold A** while auto-fire is ON: auto-firing pauses and A is **held steadily** for as long as you hold it.
  Release A and auto-firing continues.
- Auto-fire stops only when you press the turbo button again (LED back to green) or the controller disconnects.
- Speed is set by `TURBO_PERIOD_MS` in `src/main.cpp` (100 = 10/s, 66 ≈ 15/s, 50 = 20/s).
- Auto-fire is OFF after every restart.

## Status LED
| LED | Meaning |
|---|---|
| Blue blinking | waiting to pair/connect |
| Green | connected |
| Orange | connected, auto-fire ON |

## Build / flash
```
pio run -t upload
pio device monitor
```
Use the CH340K **COM** port.

The controller reports firmware revision `5.23.5.0` (a real Xbox Series controller version) instead of the library
default `0.8.0`, so macOS doesn't ask for a firmware update. **Don't try to update it** from the Xbox Accessories app:
it is an ESP32, not a real Xbox controller.

## Pairing with Mac + Parallels
1. On the Mac, **remove any old "Forgetech Pad Lite" / "Forgetech Pad Keys" pairing** (System Settings → Bluetooth → ⓘ → Forget).
   The old firmware used a different controller type and macOS may cache it.
2. Pair **Forgetech Pad Lite** with the **Mac** (System Settings → Bluetooth), not from inside Windows.
3. Start Windows in Parallels. It should appear in Control Panel → Devices and Printers as **Virtual Xbox Controller**.
4. Test in Windows with the Game Controllers panel (`joy.cpl`) or any XInput game.

Requirements (Parallels): Parallels Desktop 18+, Windows 10 or newer, and a controller the macOS Game Controller
framework accepts. Recognition of this ESP32 as an Xbox controller by macOS is based on the library documentation and
has to be confirmed on the actual Mac.

## Serial control (testing without buttons)
Every input is pressed if its physical button is pressed **or** the serial monitor says so (115200, one command per line),
so wired buttons and serial commands work together. Unwired pins simply read as released.
Several commands can go on one line, separated by `;`.

| Command | Effect |
|---|---|
| `a`, `up`, `left 500` ... | short press (150 ms by default, or the given ms) |
| `press a` / `release a` | hold / let go |
| `turbo`, `turbo on`, `turbo off` | toggle / set auto-fire |
| `reset` | release everything |
| `status`, `help` | show connection, auto-fire and what is pressed / list commands |

Names: `a b` (or `1`-`2`), `up down left right`. Example: `turbo on; press a`

A BLE report is sent only when something changes (saves battery / BLE traffic).
