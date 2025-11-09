def build_event_payload(data: dict) -> str:
    """
    Builds payload for a calendar event (vEvent).

    Example:
        {
            "type": "event",
            "data": {
                "summary": "Meeting",
                "location": "Office",
                "start": "2025-11-10T10:00:00",
                "end": "2025-11-10T11:00:00"
            }
        }
    """
    ev = data.get("data", {})
    summary = ev.get("summary", "Untitled Event")
    location = ev.get("location", "")
    start = ev.get("start", "")
    end = ev.get("end", "")

    return (
        "BEGIN:VEVENT\n"
        f"SUMMARY:{summary}\n"
        f"LOCATION:{location}\n"
        f"DTSTART:{start}\n"
        f"DTEND:{end}\n"
        "END:VEVENT"
    )
