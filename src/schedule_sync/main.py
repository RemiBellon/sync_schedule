from fetcher import download_schedule
from parser import parse_schedule
from calendar_generator import create_ics
import os

def main():
    print("--- Start synchronisation ---")

    # path
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    ods_path = os.path.join(base_dir, "data", "current_schedule.ods")
    ics_path = os.path.join(base_dir, "data", "planning_promo.ics")

    # 1: Download from NextCloud
    try:
        download_schedule()
    except Exception as e:
        print(f"Error in downloading: {e}")
        return

    # 2: Data parsing
    events = parse_schedule(ods_path)

    if not events:
        print("Error: no event was extracting")
        return

    # 3: ICS
    create_ics(events, ics_path)

    print("--- Succeed ---")
    # 4: website welcome page (index.html)
    html_path = os.path.join(base_dir, "data", "index.html")
    html_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emploi du temps PPF</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; line-height: 1.6; color: #333; }
        .code-box { background: #f4f4f4; padding: 15px; border-radius: 8px; word-break: break-all; font-family: monospace; font-size: 1.1em; }
    </style>
</head>
<body>
    <h1>Schedule PPF</h1>
    <p>The link must not be open in a browser. You must copy the link and add it to your phone calendar application as "subscription" (or something like that):</p>

    <div class="code-box">
        https://remibellon.github.io/sync_schedule/planning_promo.ics
    </div>

    <h3>iPhone (iOS)</h3>
    <ol>
        <li>Go to <b>Settings</b> > <b>Calendar</b> > <b>Accounts</b></li>
        <li>Tap <b>Add Account</b> > <b>Other</b></li>
        <li>Tap <b>Add Subscribed Calendar</b></li>
        <li>Paste the link above and tap <b>Next</b> then <b>Save</b>.</li>
    </ol>

    <h3>Android (via Google Calendar)</h3>
    <ol>
        <li>Open <b>Google Calendar</b> in your web browser.</li>
        <li>On the left panel, next to <b>Other calendars</b>, click the <b>+</b> icon.</li>
        <li>Select <b>From URL</b>.</li>
        <li>Paste the link above and click <b>Add calendar</b>.</li>
        <li>Open the Google Calendar app on your phone, and the events will sync automatically.</li>
    </ol>
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
if __name__ == "__main__":
    main()