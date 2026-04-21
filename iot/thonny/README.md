# Thonny / MicroPython Code

This folder stores MicroPython code intended for KidBright32 / ESP32-class boards.

## Files

- `kidbright32/boot.py`: boot-time setup.
- `kidbright32/main.py`: runtime loop and MQTT publish logic.
- `kidbright32/config.example.py`: config template (copy to `config.py` locally).

## Quick start

1. Copy `config.example.py` -> `config.py`.
2. Fill Wi-Fi and MQTT values.
3. Upload `boot.py`, `main.py`, and `config.py` to device via Thonny.
4. Reset board and monitor serial output.

## Important

- Do not commit `config.py` with real credentials.
