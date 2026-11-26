cmake_minimum_required(VERSION 3.13)

# Pico SDK 2.x. Point PICO_SDK_PATH at it (the VS Code Pico extension keeps one
# in ~/.pico-sdk/sdk/<version>).
include(pico_sdk_import.cmake)

project(dock_selftest C CXX ASM)
set(CMAKE_C_STANDARD 11)

# The dock copies the Pico's flash setup (W25Q-series QSPI, 2 MB, 12 MHz crystal).
set(PICO_BOARD pico CACHE STRING "")
pico_sdk_init()

add_executable(dock_selftest main.c)
target_link_libraries(dock_selftest pico_stdlib pico_unique_id hardware_adc hardware_flash hardware_clocks)

pico_enable_stdio_usb(dock_selftest 1)
pico_enable_stdio_uart(dock_selftest 0)
target_compile_definitions(dock_selftest PRIVATE
    PICO_STDIO_USB_CONNECT_WAIT_TIMEOUT_MS=0
    USBD_PRODUCT="WakeBand dock self-test")

pico_add_extra_outputs(dock_selftest)
