from icalendar import Calendar, Event, vText
from datetime import datetime
import pytz
import os

def create_ics(events: list, output_path: str):
    """
    Take a list of dict to generate .ics file.
    """
    print(f"Schedule generation: {len(events)}")

    # Creation of the main schedule object
    cal = Calendar()

    # Parameters commandable for iCalendar
    cal.add('prodid', '-//Schedule PPF 2026//FR')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Planning PPF 2026') # Name displayed on phones
    cal.add('x-wr-timezone', 'Europe/Paris')

    # France timezone
    tz = pytz.timezone('Europe/Paris')

    for evt_data in events:
        # Extract hours from string (ex: "09:00-12:15")
        time_str = evt_data.get('time', '')
        if "-" not in time_str:
            continue

        start_time_str, end_time_str = time_str.split('-')

        # Clean date display (ex: '2026-09-02 00:00:00' becomes '2026-09-02')
        date_only_str = evt_data['date'].split(' ')[0]

        # Datetime objects construction
        try:
            # Starting date
            dt_start = datetime.strptime(f"{date_only_str} {start_time_str.strip()}", "%Y-%m-%d %H:%M")
            dt_start = tz.localize(dt_start)

            # End date
            dt_end = datetime.strptime(f"{date_only_str} {end_time_str.strip()}", "%Y-%m-%d %H:%M")
            dt_end = tz.localize(dt_end)
        except ValueError as e:
            print(f"Erreur de format de date pour l'événement {evt_data['course']}: {e}")
            continue

        # iCalendar event creation
        event = Event()

        # Course ("Title")
        title = evt_data['course']
        if evt_data['professor'] and evt_data['professor'] != 'nan':
            title += f" ({evt_data['professor']})"
        event.add('summary', title)

        # Dates
        event.add('dtstart', dt_start)
        event.add('dtend', dt_end)

        # Date creation
        event.add('dtstamp', tz.localize(datetime.now()))

        # Localisation
        if evt_data['location'] and evt_data['location'] != 'nan':
            event.add('location', vText(evt_data['location']))

        # Event unique ID (if needed to be update or not)
        uid_string = f"{date_only_str}-{time_str}-{evt_data['course']}@planning-ppf.fr"
        event.add('uid', uid_string.replace(' ', ''))

        # Add event to main calendar
        cal.add_component(event)

    # Save file .ics
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(cal.to_ical())

    print(f"Calendar generated: {output_path}")


if __name__ == "__main__":
    # Iintégration test with parser
    from parser import parse_schedule

    # parse ODS
    mes_cours = parse_schedule("../../data/current_schedule.ods") #

    # 2. Generation ICS
    create_ics(mes_cours, "../../data/planning_promo.ics")