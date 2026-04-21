import logging

from services import actuators


def test_actuator_helpers_emit_log_messages(caplog):
    with caplog.at_level(logging.INFO):
        actuators.set_pump(True)
        actuators.set_light(True, "blue")
        actuators.set_humidifier(False)

    logs = "\n".join(caplog.messages)
    assert "Pump" in logs
    assert "Light" in logs
    assert "Humidifier" in logs
