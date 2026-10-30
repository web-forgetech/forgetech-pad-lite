#pragma once
// ESP32-C3-MINI-1 dev board (CH340K COM port, RGB LED on GPIO8)
// All inputs: wire to GND, internal pull-ups used

// Face buttons
#define PIN_BTN_A   5
#define PIN_BTN_B   6
#define PIN_BTN_X   10
#define PIN_BTN_Y   18   // native USB D- pin used as GPIO: the "ESP32-C3 USB" port stops working,
                         // upload/Serial via the CH340K COM port is unaffected. GPIO19 is still free.

// Direction buttons (reported as the Xbox LEFT analog stick)
#define PIN_UP      0
#define PIN_DOWN    1
#define PIN_LEFT    3
#define PIN_RIGHT   4

// Turbo button: GPIO7 -> GND (not a strapping pin, safe at boot)
//   each press = auto-fire on/off (A fires by itself; holding A = steady hold)
#define PIN_TURBO   7

// Onboard WS2812 RGB LED
#define PIN_RGB     8
