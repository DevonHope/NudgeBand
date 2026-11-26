/*
 * WakeBand dock self-test (RP2040, dock PCB rev B / rev C).
 *
 * A bring-up check for a freshly assembled dock, before it gets its real
 * firmware (Raspberry Pi debugprobe). It only uses the dock's own parts:
 * take the band out of the dock while this runs.
 *
 * What the two red LEDs mean (D1 = "USB", GPIO2; D2 = "ACT", GPIO16):
 *
 *   Start-up (about 3 s)
 *     both on for 1 s            lamp test: both LEDs and their resistors work
 *     D1, D2, D1, D2 ...         each LED on its own, three times
 *
 *   Afterwards, D1 (USB)
 *     solid                      the computer has set up the USB connection
 *     slow blink (1 per second)  powered, but no computer has set up USB
 *                                (a phone charger, or a bad data line)
 *
 *   Afterwards, D2 (ACT)
 *     one short flash every 2 s  every test passed
 *     N quick flashes, pause     test number N failed (the first one that did)
 *
 * Tests (numbers are the D2 blink count on failure):
 *   1  flash chip answers with the W25Q16JV ID (EF 40 15)
 *   2  flash erase / write / read back of the last 4 KB sector
 *   3  12 MHz crystal runs at 12 MHz (+-1 %)
 *   4  SWDIO path: GPIO14 drives through R10, GPIO13 reads the same level
 *   5  SWDIO translator (TXS0101) holds the idle line high, so it has
 *      both its 3.3 V and 1.8 V supplies
 *   6  SWCLK pull-down (R15) holds GPIO12 low when nothing drives it
 *
 * The same report is printed on the USB serial port (any terminal, any baud)
 * every 5 s. Type 'r' to run the tests again, 'b' to restart into the
 * RPI-RP2 boot drive (so you can copy debugprobe.uf2 without the BOOTSEL
 * button). Opening the port at 1200 baud also restarts into the boot drive.
 */
#include <stdio.h>
#include <string.h>

#include "pico/stdlib.h"
#include "pico/bootrom.h"
#include "hardware/adc.h"
#include "hardware/clocks.h"
#include "hardware/flash.h"
#include "hardware/sync.h"
#include "pico/unique_id.h"
#include "tusb.h"

#define PIN_LED_USB 2
#define PIN_LED_ACT 16
#define PIN_SWCLK 12
#define PIN_SWDI 13
#define PIN_SWDIO 14

#define N_TESTS 6

static const char *const test_name[N_TESTS + 1] = {
    "",
    "flash ID (W25Q16JV, EF 40 15)",
    "flash erase/write/read last sector",
    "12 MHz crystal frequency",
    "SWDIO drive (GPIO14) -> read back (GPIO13)",
    "SWDIO translator pull-up (TXS0101 powered, 1.8 V rail)",
    "SWCLK pull-down (R15) holds GPIO12 low",
};

static bool result[N_TESTS + 1];
static char detail[N_TESTS + 1][64];
static int first_fail;

/* ---- tests ---------------------------------------------------------- */

static bool t_flash_id(char *d) {
    uint8_t tx[4] = {0x9f, 0, 0, 0}, rx[4] = {0};
    uint32_t irq = save_and_disable_interrupts();
    flash_do_cmd(tx, rx, 4);
    restore_interrupts(irq);
    snprintf(d, 64, "got %02X %02X %02X", rx[1], rx[2], rx[3]);
    return rx[1] == 0xEF && rx[2] == 0x40 && rx[3] == 0x15;
}

#define TEST_OFFSET (PICO_FLASH_SIZE_BYTES - FLASH_SECTOR_SIZE)

static bool t_flash_rw(char *d) {
    static uint8_t buf[FLASH_PAGE_SIZE];
    const uint8_t *xip = (const uint8_t *)(XIP_BASE + TEST_OFFSET);
    uint32_t seed = time_us_32();

    for (int i = 0; i < FLASH_PAGE_SIZE; i++)
        buf[i] = (uint8_t)(seed >> (i % 4 * 8)) ^ (uint8_t)i;

    uint32_t irq = save_and_disable_interrupts();
    flash_range_erase(TEST_OFFSET, FLASH_SECTOR_SIZE);
    restore_interrupts(irq);
    for (int i = 0; i < FLASH_SECTOR_SIZE; i++) {
        if (xip[i] != 0xff) {
            snprintf(d, 64, "erase: byte %d is %02X", i, xip[i]);
            return false;
        }
    }
    irq = save_and_disable_interrupts();
    flash_range_program(TEST_OFFSET, buf, FLASH_PAGE_SIZE);
    restore_interrupts(irq);
    if (memcmp(xip, buf, FLASH_PAGE_SIZE) != 0) {
        snprintf(d, 64, "read back differs from what was written");
        return false;
    }
    snprintf(d, 64, "%d bytes at 0x%06X ok", FLASH_PAGE_SIZE, TEST_OFFSET);
    return true;
}

static bool t_xosc(char *d) {
    uint32_t khz = frequency_count_khz(CLOCKS_FC0_SRC_VALUE_XOSC_CLKSRC);
    snprintf(d, 64, "%lu kHz", (unsigned long)khz);
    return khz > 11880 && khz < 12120;
}

static bool t_swdio_loop(char *d) {
    gpio_init(PIN_SWDI);
    gpio_set_dir(PIN_SWDI, GPIO_IN);
    gpio_disable_pulls(PIN_SWDI);
    gpio_init(PIN_SWDIO);
    gpio_set_dir(PIN_SWDIO, GPIO_OUT);

    bool ok = true;
    int lo = -1, hi = -1;
    for (int k = 0; k < 4; k++) {
        gpio_put(PIN_SWDIO, 0);
        sleep_us(50);
        lo = gpio_get(PIN_SWDI);
        gpio_put(PIN_SWDIO, 1);
        sleep_us(50);
        hi = gpio_get(PIN_SWDI);
        if (lo != 0 || hi != 1) ok = false;
    }
    gpio_set_dir(PIN_SWDIO, GPIO_IN); /* release the line */
    snprintf(d, 64, "drive 0 -> read %d, drive 1 -> read %d", lo, hi);
    return ok;
}

static bool t_swdio_pullup(char *d) {
    gpio_init(PIN_SWDIO);
    gpio_set_dir(PIN_SWDIO, GPIO_IN);
    gpio_disable_pulls(PIN_SWDIO);
    gpio_init(PIN_SWDI);
    gpio_set_dir(PIN_SWDI, GPIO_IN);
    gpio_pull_down(PIN_SWDI); /* ~50 k: loses to the TXS0101's 10 k pull-up */
    sleep_ms(2);
    int v = gpio_get(PIN_SWDI);
    gpio_disable_pulls(PIN_SWDI);
    snprintf(d, 64, "idle line with RP2040 pull-down reads %d", v);
    return v == 1;
}

static bool t_swclk_pulldown(char *d) {
    gpio_init(PIN_SWCLK);
    gpio_set_dir(PIN_SWCLK, GPIO_OUT);
    gpio_put(PIN_SWCLK, 1); /* charge the node high first */
    sleep_us(20);
    gpio_set_dir(PIN_SWCLK, GPIO_IN);
    gpio_disable_pulls(PIN_SWCLK);
    sleep_ms(2); /* 100 k x a few pF settles in microseconds */
    int v = gpio_get(PIN_SWCLK);
    snprintf(d, 64, "released line reads %d", v);
    return v == 0;
}

static void run_tests(void) {
    bool (*const fn[N_TESTS + 1])(char *) = {
        NULL, t_flash_id, t_flash_rw, t_xosc, t_swdio_loop, t_swdio_pullup, t_swclk_pulldown,
    };
    first_fail = 0;
    for (int i = 1; i <= N_TESTS; i++) {
        detail[i][0] = 0;
        result[i] = fn[i](detail[i]);
        if (!result[i] && !first_fail) first_fail = i;
    }
}

static float die_temp_c(void) {
    adc_select_input(4);
    float v = adc_read() * 3.3f / 4096.0f;
    return 27.0f - (v - 0.706f) / 0.001721f;
}

static void print_report(void) {
    char id[2 * PICO_UNIQUE_BOARD_ID_SIZE_BYTES + 1];
    pico_get_unique_board_id_string(id, sizeof id);
    printf("\n=== WakeBand dock self-test ===\n");
    printf("board id %s, die %.1f C, clk_sys %lu kHz\n", id, die_temp_c(),
           (unsigned long)frequency_count_khz(CLOCKS_FC0_SRC_VALUE_CLK_SYS));
    for (int i = 1; i <= N_TESTS; i++)
        printf("  %d %-4s %-55s %s\n", i, result[i] ? "PASS" : "FAIL", test_name[i], detail[i]);
    if (first_fail)
        printf("RESULT: FAIL (ACT LED blinks %d times)\n", first_fail);
    else
        printf("RESULT: all %d passed (ACT LED: one flash every 2 s)\n", N_TESTS);
    printf("keys: r = run again, b = restart into the RPI-RP2 boot drive\n");
}

/* ---- LEDs ----------------------------------------------------------- */

static void leds(bool usb, bool act) {
    gpio_put(PIN_LED_USB, usb);
    gpio_put(PIN_LED_ACT, act);
}

static void lamp_test(void) {
    leds(1, 1);
    sleep_ms(1000);
    for (int i = 0; i < 3; i++) {
        leds(1, 0);
        sleep_ms(250);
        leds(0, 1);
        sleep_ms(250);
    }
    leds(0, 0);
    sleep_ms(300);
}

/* ACT pattern, one frame per 50 ms tick. */
static bool act_level(uint32_t tick) {
    if (!first_fail) {
        return (tick % 40) < 2; /* 100 ms flash every 2 s */
    }
    uint32_t period = (uint32_t)first_fail * 5 + 30; /* N x 250 ms, then 1.5 s off */
    uint32_t t = tick % period;
    return t < (uint32_t)first_fail * 5 && (t % 5) < 2;
}

int main(void) {
    gpio_init(PIN_LED_USB);
    gpio_set_dir(PIN_LED_USB, GPIO_OUT);
    gpio_init(PIN_LED_ACT);
    gpio_set_dir(PIN_LED_ACT, GPIO_OUT);
    adc_init();
    adc_set_temp_sensor_enabled(true);

    lamp_test();
    run_tests(); /* before USB starts, so the flash test has the bus to itself */

    stdio_init_all();

    uint32_t tick = 0;
    absolute_time_t next_report = make_timeout_time_ms(1500);
    while (true) {
        bool mounted = tud_mounted();
        bool usb_led = mounted ? true : ((tick % 20) < 10);
        leds(usb_led, act_level(tick));

        int c = getchar_timeout_us(0);
        if (c == 'r' || c == 'R') {
            leds(0, 0);
            /* single core: the flash test masks interrupts, so USB just
             * pauses for the ~50 ms sector erase */
            run_tests();
            next_report = make_timeout_time_ms(1500);
        } else if (c == 'b' || c == 'B') {
            printf("restarting into the RPI-RP2 boot drive\n");
            sleep_ms(100);
            reset_usb_boot(0, 0);
        }

        if (time_reached(next_report)) {
            print_report();
            next_report = make_timeout_time_ms(5000);
        }
        sleep_ms(50);
        tick++;
    }
}
