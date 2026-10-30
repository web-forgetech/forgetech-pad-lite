// ForgeTech Pad Lite - ESP32-C3 BLE Xbox controller: A/B/X/Y + left stick + auto-fire (turbo) on A
// Emulates an Xbox Series X Wireless Controller (XInput, VID 0x045E / PID 0x0B13), so it works on
// macOS (Game Controller framework), Windows, and Windows in Parallels (shared as "Virtual Xbox Controller").
// Each input = physical button OR serial command (see README.md)
#include <Arduino.h>
#include <BleGamepad.h>
#include "pins.h"

#define DEVICE_NAME "ForgeTech Pad Lite"
#define FW_VERSION  "1.4"   // 1.4 = X/Y buttons; 1.3 = ForgeTech branding; 1.2 = self-firing auto-fire
BleGamepad gamepad(DEVICE_NAME, "ForgeTech", 100);

const uint8_t  DEBOUNCE_MS     = 20;
const uint16_t TAP_MS          = 150;
const uint16_t TURBO_PERIOD_MS = 100;   // auto-fire on A: 10 shots per second (50 ms on / 50 ms off)

// Active-low button (pin to GND, internal pull-up) with debounce
struct Debounced {
  uint8_t pin; bool raw; bool stable; uint32_t changedAt;
  bool update() {
    bool r = !digitalRead(pin);
    if (r != raw) { raw = r; changedAt = millis(); }
    else if (millis() - changedAt >= DEBOUNCE_MS) stable = raw;
    return stable;
  }
};

// 4 face buttons + 4 direction buttons. held/tapUntil are set from Serial.
struct Input { Debounced btn; const char* name; bool held; uint32_t tapUntil; bool state; };
Input inputs[] = {
  {{PIN_BTN_A}, "a"}, {{PIN_BTN_B}, "b"}, {{PIN_BTN_X}, "x"}, {{PIN_BTN_Y}, "y"},
  {{PIN_UP}, "up"}, {{PIN_DOWN}, "down"}, {{PIN_LEFT}, "left"}, {{PIN_RIGHT}, "right"},
};
const uint8_t NUM_IN = sizeof(inputs) / sizeof(inputs[0]);
const uint8_t NUM_BTN = 4;   // first 4 inputs are buttons: BUTTON_1..4 = Xbox A, B, X, Y
enum { A = 0, B, X, Y, UP, DOWN, LEFT, RIGHT };

Debounced turboBtn = {PIN_TURBO};
bool turbo = false;

// Physical pin OR serial; unwired pins float HIGH (pull-up) and read as released
bool isPressed(const Input& in) {
  return in.btn.stable || in.held || (int32_t)(in.tapUntil - millis()) > 0;
}

// Input by name (a, up...) or button number (1-4); -1 if unknown
int findInput(const char* s) {
  if (!s) return -1;
  for (uint8_t i = 0; i < NUM_IN; i++) if (!strcasecmp(s, inputs[i].name)) return i;
  int n = atoi(s);
  return (n >= 1 && n <= NUM_BTN) ? n - 1 : -1;
}

void setTurbo(bool on) {
  turbo = on;
  Serial.printf("auto-fire %s%s\n", on ? "ON" : "OFF",
                on && !gamepad.isConnected() ? " (starts firing once a computer is connected)" : "");
}

uint32_t reportsSent = 0;   // shown by 'status' - should climb ~20/s while auto-fire is running

// RGB status: blue blink = waiting to pair, green = connected, orange = connected + auto-fire on A
void statusLed(bool connected) {
  static uint32_t t = 0;
  static bool on = false;
  if (millis() - t < (connected ? 100 : 500)) return;
  t = millis();
  if (connected) rgbLedWrite(PIN_RGB, turbo ? 20 : 0, turbo ? 6 : 20, 0);
  else { on = !on; rgbLedWrite(PIN_RGB, 0, 0, on ? 20 : 0); }
}

// Direction buttons -> Xbox LEFT analog stick (full tilt; opposite directions cancel out).
// Range -32767..32767, centre 0, up = negative Y (HID convention).
// Diagonals use 0.707 x full so the stick stays on a circle like a real thumbstick.
const int16_t STICK_FULL = 32767;
const int16_t STICK_DIAG = 23170;   // 32767 * 0.7071

void stickXY(int16_t& x, int16_t& y) {
  int8_t dx = (inputs[RIGHT].state ? 1 : 0) - (inputs[LEFT].state ? 1 : 0);
  int8_t dy = (inputs[DOWN].state ? 1 : 0) - (inputs[UP].state ? 1 : 0);
  int16_t mag = (dx && dy) ? STICK_DIAG : STICK_FULL;
  x = dx * mag;
  y = dy * mag;
}

void sendState() {
  inputs[A].state ? gamepad.press(BUTTON_1) : gamepad.release(BUTTON_1);   // Xbox A
  inputs[B].state ? gamepad.press(BUTTON_2) : gamepad.release(BUTTON_2);   // Xbox B
  inputs[X].state ? gamepad.press(BUTTON_3) : gamepad.release(BUTTON_3);   // Xbox X
  inputs[Y].state ? gamepad.press(BUTTON_4) : gamepad.release(BUTTON_4);   // Xbox Y
  int16_t x, y;
  stickXY(x, y);
  gamepad.setLeftThumb(x, y);
  gamepad.setHat1(HAT_CENTERED);     // Xbox D-pad not used
  gamepad.sendReport();
  reportsSent++;
}

void printHelp() {
  Serial.println(F(
    "\nSerial commands (separate several with ';'):\n"
    "  <name> [ms]          tap, e.g. 'a' or 'up 500' (default 150 ms)\n"
    "  press <name>         hold\n"
    "  release <name>       let go\n"
    "  turbo [on|off]       auto-fire: A fires by itself; hold A = steady hold (no argument = toggle)\n"
    "  reset                release everything\n"
    "  status               show what is pressed\n"
    "  names: a b x y (or 1-4), up down left right\n"
    "  example: turbo on   (then: press a / release a)"));
}

void printStatus() {
  Serial.printf("fw=%s  connected=%s  auto-fire=%s  reports-sent=%lu  pressed:", FW_VERSION,
                gamepad.isConnected() ? "yes" : "no", turbo ? "on" : "off", (unsigned long)reportsSent);
  for (uint8_t i = 0; i < NUM_IN; i++) if (isPressed(inputs[i])) Serial.printf(" %s", inputs[i].name);
  Serial.println();
}

void handleCommand(char* line) {
  char* save;
  char* cmd = strtok_r(line, " \t", &save);
  if (!cmd) return;
  char* a1 = strtok_r(nullptr, " \t", &save);
  int i;
  bool isPress = !strcasecmp(cmd, "press"), isRelease = !strcasecmp(cmd, "release");

  if (!strcasecmp(cmd, "help") || !strcmp(cmd, "?")) printHelp();
  else if (!strcasecmp(cmd, "status")) printStatus();
  else if (!strcasecmp(cmd, "turbo")) {
    if (!a1) setTurbo(!turbo);
    else if (!strcasecmp(a1, "on")) setTurbo(true);
    else if (!strcasecmp(a1, "off")) setTurbo(false);
    else Serial.println("? use: turbo, turbo on, turbo off");
  }
  else if (!strcasecmp(cmd, "reset")) {
    for (Input& in : inputs) { in.held = false; in.tapUntil = 0; }
    Serial.println("ok");
  }
  else if (isPress || isRelease) {
    if ((i = findInput(a1)) < 0) { Serial.printf("? unknown name: '%s'\n", a1 ? a1 : ""); return; }
    inputs[i].held = isPress;
    if (isRelease) inputs[i].tapUntil = 0;
    Serial.println("ok");
  }
  else if ((i = findInput(cmd)) >= 0) { inputs[i].tapUntil = millis() + (a1 ? atoi(a1) : TAP_MS); Serial.println("ok"); }
  else Serial.printf("? unknown: '%s' (type 'help')\n", cmd);
}

// Collect characters into a line; accepts \n, \r or \r\n endings
void pollSerial() {
  static char buf[96];
  static uint8_t len = 0;
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (!len) continue;
      buf[len] = '\0';
      len = 0;
      char* save;
      for (char* part = strtok_r(buf, ";", &save); part; part = strtok_r(nullptr, ";", &save)) handleCommand(part);
    } else if (len < sizeof(buf) - 1) {
      buf[len++] = c;
    }
  }
}

void setup() {
  Serial.begin(115200);
  for (uint8_t i = 0; i < NUM_IN; i++) pinMode(inputs[i].btn.pin, INPUT_PULLUP);
  pinMode(PIN_TURBO, INPUT_PULLUP);

  BleGamepadConfiguration cfg;
  cfg.setGamepadMode(GamepadMode::XInputSeriesX);   // sets Xbox VID/PID, buttons, D-pad, sticks
  cfg.setAutoReport(false);
  // Report a real Xbox Series controller firmware version (library default "0.8.0" makes
  // macOS show "firmware out of date"). The ESP32 itself is NOT updated by this.
  cfg.setFirmwareRevision("5.23.5.0");
  gamepad.begin(&cfg);
  Serial.println("ForgeTech Pad Lite firmware " FW_VERSION " - BLE Xbox controller, pair as '" DEVICE_NAME "'");
  printHelp();
}

void loop() {
  pollSerial();  // works even before a host connects

  // Read all buttons (debounced); turbo button toggles auto-fire on each press
  for (Input& in : inputs) in.btn.update();
  bool turboWasDown = turboBtn.stable;
  if (turboBtn.update() && !turboWasDown) setTurbo(!turbo);

  static bool wasConnected = false;
  bool connected = gamepad.isConnected();
  statusLed(connected);
  if (!connected) { wasConnected = false; delay(5); return; }

  bool changed = !wasConnected;   // send a full report right after (re)connecting
  wasConnected = true;

  // Auto-fire ON: A fires by itself (pressed in the first half of each period), no need to hold it.
  // If the user presses and holds A, auto-fire pauses and A is held steadily until released;
  // after release, auto-fire continues until the turbo button turns it off.
  bool firePhase = (millis() % TURBO_PERIOD_MS) < TURBO_PERIOD_MS / 2;

  for (uint8_t i = 0; i < NUM_IN; i++) {
    bool p = isPressed(inputs[i]);
    if (turbo && i == A && !p) p = firePhase;
    if (p != inputs[i].state) { inputs[i].state = p; changed = true; }
  }

  if (changed) sendState();   // only when something changed (saves battery / BLE traffic)
  delay(5);
}
