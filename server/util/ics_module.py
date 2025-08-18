from ics import Calendar, Event
from datetime import timedelta

class ICSModule:
    def __init__(self):
        self.calendar = Calendar()

    def create_event(self, name, begin, end, description, recurrence=None, reminder=None):
        """
        Create a calendar event.
        :param name: Event name.
        :param begin: Start time.
        :param end: End time.
        :param description: Event description.
        :param recurrence: Recurrence rule (e.g., "RRULE:FREQ=DAILY;COUNT=5").
        :param reminder: Reminder time before the event (e.g., timedelta(minutes=30)).
        """
        if begin >= end:
            raise ValueError("Event start time must be before end time.")

        event = Event()
        event.name = name
        event.begin = begin
        event.end = end
        event.description = description

        if recurrence:
            event.extra.append(recurrence)

        if reminder:
            event.extra.append(f"BEGIN:VALARM\nTRIGGER:-P{reminder.total_seconds()}S\nACTION:DISPLAY\nDESCRIPTION:{name}\nEND:VALARM")

        self.calendar.events.add(event)

    def save_calendar(self, file_name):
        """
        Save the calendar to a .ics file.
        :param file_name: File name for the .ics file.
        """
        with open(file_name, "w") as file:
            file.writelines(self.calendar)

# Example usage
if __name__ == "__main__":
    ics_module = ICSModule()
    ics_module.create_event(
        "Meeting", "2025-08-18 10:00:00", "2025-08-18 11:00:00", "Discuss rider clauses.",
        recurrence="RRULE:FREQ=DAILY;COUNT=5", reminder=timedelta(minutes=30)
    )
    ics_module.save_calendar("planner-event.ics")
