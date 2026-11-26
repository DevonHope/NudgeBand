# Dock self-test firmware

A bring-up check for a freshly assembled dock PCB (rev B or rev C), run once before the dock gets its real
firmware, Raspberry Pi's [debugprobe](https://github.com/raspberrypi/debugprobe). It checks the dock's own
parts and shows the result on the two red LEDs, so it works without a computer once flashed. **Take the band
out of the dock while it runs.**

## Flash it

1. Plug the dock into a computer. A blank dock comes up as the `RPI-RP2` drive by itself (otherwise hold
   BOOTSEL, SW1, while plugging in).
2. Copy `dock_selftest.uf2` onto the drive. The dock restarts into the test.

## What the LEDs mean

D1 is the LED marked USB (GPIO2), D2 the one marked ACT (GPIO16).

| When | LED | Pattern | Meaning |
| --- | --- | --- | --- |
| first ~3 s | both | on together for 1 s | lamp test: both LEDs work |
| | both | D1, D2, D1, D2 ... (3 times) | each LED on its own |
| after | D1 (USB) | solid | a computer has set up the USB connection |
| | D1 (USB) | slow blink, once a second | powered, but USB is not set up (a charger, or a bad data line) |
| | D2 (ACT) | one short flash every 2 s | every test passed |
| | D2 (ACT) | N quick flashes, then a pause | test N failed (the first that did) |
| | both off | | no power, or the firmware is not running (check the flash) |

| # | Test | A failure points at |
| --- | --- | --- |
| 1 | flash chip answers with the W25Q16JV ID (EF 40 15) | U2 or the QSPI lines |
| 2 | erase, write and read back the flash's last 4 KB sector | U2, its supply or decoupling |
| 3 | the crystal runs at 12 MHz (within 1 %) | Y1, C1/C2, R1 |
| 4 | GPIO14 drives SWDIO through R10 and GPIO13 reads the same level | R10, RP2040 pins 16/17 |
| 5 | the TXS0101 holds the idle SWDIO line high (it has both its 3.3 V and 1.8 V supplies) | U8, U5 (1.8 V) |
| 6 | R15 pulls the released SWCLK line low | R15 |

Test 2 rewrites the last flash sector, which nothing else on the dock uses.

## Report over USB

The dock also shows up as a USB serial port ("WakeBand dock self-test") and prints the full report every
5 s. In any terminal: `r` runs the tests again, `b` restarts into the `RPI-RP2` drive, so debugprobe can be
copied on without the BOOTSEL button. Opening the port at 1200 baud does the same.

## Build

Pico SDK 2.x (the VS Code Pico extension installs one in `~/.pico-sdk`):

```sh
export PICO_SDK_PATH=~/.pico-sdk/sdk/2.2.0
cmake -S firmware/dock-selftest -B build/dock-selftest -G Ninja
cmake --build build/dock-selftest   # -> build/dock-selftest/dock_selftest.uf2
```

## Then: the real firmware

Copy `debugprobe.uf2` (the Debug Probe build, not `debugprobe_on_pico.uf2`) from the latest
[debugprobe release](https://github.com/raspberrypi/debugprobe/releases) onto the `RPI-RP2` drive. Its pin
map (SWCLK GPIO12, SWDI GPIO13, SWDIO GPIO14, LEDs GPIO2 and GPIO16) is the one the dock copies; checked
against v2.3.1. Under debugprobe, D1 is on while USB is connected and D2 flickers while a tool talks to the
band. The band's 5 V supply needs no firmware: the SY6280 switch is always on.
