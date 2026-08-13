from app.safety import critical_rule


def test_exposed_wiring_triggers():
    assert critical_rule("Exposed electrical wires are hanging beside the laboratory entrance.") == "ELECTRICAL_DANGER"


def test_wifi_does_not_trigger():
    assert critical_rule("The Wi-Fi in Library Level 2 disconnects every few minutes.") is None
