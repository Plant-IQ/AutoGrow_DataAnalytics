import logging
logging.basicConfig(level=logging.INFO)

def set_pump(on: bool):
    logging.info(f"[MOCK] Pump → {'ON' if on else 'OFF'}")

def set_light(on: bool, color: str = "blue"):
    logging.info(f"[MOCK] Light → {'ON' if on else 'OFF'} | spectrum: {color}")

def set_humidifier(on: bool):
    logging.info(f"[MOCK] Humidifier → {'ON' if on else 'OFF'}")