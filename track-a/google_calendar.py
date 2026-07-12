"""
Google Calendar API integration for Smart Academic OS.

Handles OAuth2 authentication, event creation/fetching,
conflict checking, with service caching and structured logging.
"""

import datetime
import os.path
import logging

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']

_service_cache = None
_credentials = None


def get_service():
    """Get or create Google Calendar API service with caching."""
    global _service_cache, _credentials

    # Reuse cached service if credentials are still valid
    if _service_cache is not None and _credentials is not None:
        try:
            if _credentials.valid:
                return _service_cache
            elif _credentials.expired and _credentials.refresh_token:
                from google.auth.transport.requests import Request
                _credentials.refresh(Request())
                _service_cache = None  # Force rebuild
        except Exception as e:
            logger.warning("Credential refresh failed, re-authenticating: %s", e)
            _service_cache = None

    creds = None
    if os.path.exists('token.json'):
        try:
            from google.oauth2.credentials import Credentials
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            logger.warning("Failed to load token.json: %s", e)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
            except Exception as e:
                logger.error("Token refresh failed: %s", e)
                return None
        else:
            try:
                from google_auth_oauthlib.flow import InstalledAppFlow
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            except FileNotFoundError:
                logger.error("credentials.json not found — Google Calendar not configured")
                return None
            except Exception as e:
                logger.error("OAuth flow failed: %s", e)
                return None
            try:
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                logger.warning("Failed to save token.json: %s", e)

    _credentials = creds
    from googleapiclient.discovery import build
    _service_cache = build('calendar', 'v3', credentials=creds)
    logger.info("Google Calendar service initialized")
    return _service_cache


def create_event(title: str, start_time: str, end_time: str):
    """Create a Google Calendar event."""
    service = get_service()
    if service is None:
        logger.warning("Google Calendar not available")
        return None

    from core.config import Settings
    timezone = Settings.TIMEZONE

    event = {
        'summary': str(title)[:200],
        'start': {
            'dateTime': start_time,
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_time,
            'timeZone': timezone,
        },
    }

    try:
        result = service.events().insert(calendarId='primary', body=event).execute()
        logger.info("Created Google Calendar event: %s", title[:50])
        return result
    except Exception as e:
        logger.error("Failed to create Google Calendar event: %s", e)
        return None


def get_events(max_results: int = 10):
    """Fetch upcoming Google Calendar events."""
    service = get_service()
    if service is None:
        return []

    try:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        events = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=min(max_results, 50),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events.get('items', [])
    except Exception as e:
        logger.error("Failed to fetch Google Calendar events: %s", e)
        return []


def check_conflict(start_time: str, end_time: str):
    """Check if a time slot conflicts with existing events."""
    service = get_service()
    if service is None:
        return False, None

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
        logger.error("Conflict check error: %s", e)
        return False, None
