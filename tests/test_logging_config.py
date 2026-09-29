from app.logging_config import scrub_event


def test_scrub_event_redacts_pii_in_nested_log_values() -> None:
    record = {
        "event": "request_received",
        "payload": {
            "message_preview": (
                "student@example.com 0901234567 012345678901 4111-1111-1111-1111"
            ),
            "nested": ["Contact +84 90 123 4567"],
        },
    }

    scrubbed = scrub_event(None, "", record)

    serialized = str(scrubbed)
    for raw_value in (
        "student@example.com",
        "0901234567",
        "012345678901",
        "4111-1111-1111-1111",
        "+84 90 123 4567",
    ):
        assert raw_value not in serialized
    assert "REDACTED_EMAIL" in serialized
    assert "REDACTED_PHONE_VN" in serialized
    assert "REDACTED_CCCD" in serialized
    assert "REDACTED_CREDIT_CARD" in serialized
