import datetime
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_service():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service


def create_event(title, start_time, end_time):
    service = get_service()

    event = {
        'summary': title,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Kolkata',
        },
    }

    return service.events().insert(calendarId='primary', body=event).execute()


def get_events():
    service = get_service()

    now = datetime.datetime.utcnow().isoformat() + 'Z'

    events = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    return events.get('items', [])
def check_conflict(start_time, end_time):
    service = get_service()

    try:
        events = service.events().list(
            calendarId='primary',
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True
        ).execute()

        items = events.get('items', [])

        if items:
            return True, items[0].get('summary', 'Unknown Event')

        return False, None

    except Exception as e:
        print("Conflict Error:", e)
        return False, None