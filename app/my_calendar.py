import os
from datetime import datetime, timedelta, date, time
from typing import Optional
from zoneinfo import ZoneInfo

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/calendar"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials", "credentials.json")
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")

class CalendarNotConfigure(Exception):
    pass
class CalendarControl:
    def __init__(self):
        self.service = self._authenticate() # Service active to Google Calendar API
        self.time_zone = 'Europe/Bratislava' # Timezone
        self.calendar_id = "primary" # Writing to Calendar

#  Convert Google datetime
    def _to_rfc3339(self, d: date, t: time) -> str:
        dt = datetime.combine(d, t).replace(tzinfo=ZoneInfo(self.time_zone))
        return dt.isoformat()
    @staticmethod # immutable method(indepedent)
    def _authenticate():
        # Launches the OAuth2 authentication flow in the default browser
        if not os.path.exists(CREDENTIALS_PATH):
            raise CalendarNotConfigure("Credentials not configured")
        creds = None
        if not os.path.exists(TOKEN_PATH):
            raise CalendarNotConfigure("Token not configured")
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=8080, open_browser=False)
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())
        return build("calendar", "v3", credentials=creds)

# CRUD

    def add_event(self, title,start: time,end: time, d: date) -> dict | None:
        if start >= end:
            raise Exception("start must be before end")
        body = {"summary": title,"start":{"dateTime": self._to_rfc3339(d,start), "timeZone": self.time_zone},
                "end": {"dateTime": self._to_rfc3339(d,end),"timeZone": self.time_zone}
                }
        return self.service.events().insert(calendarId=self.calendar_id, body=body).execute()

    def delete_event(self, event_id: str)-> None:
        self.service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()
    def list_events(self, d: Optional[date] = None):
        params = {"calendarId": self.calendar_id, "singleEvents": True, "orderBy": "startTime", "maxResults":50}
        if d:
            start_dt = datetime.combine(d, time(0,0)).replace(tzinfo=ZoneInfo(self.time_zone))
            end_dt = start_dt + timedelta(days=1)
            params.update({"timeMin":start_dt.isoformat(), "timeMax":end_dt.isoformat()})
        else:
            now = datetime.now(ZoneInfo(self.time_zone))
            params["timeMin"] = now.isoformat()
        res = self.service.events().list(**params).execute()
        return res.get("items", [])
    def get_event(self, event_id: str):
        return self.service.events().get(calendarId=self.calendar_id, eventId=event_id).execute()

    def update_event(self, event_id: str, title: Optional[str] = None, start: Optional[time]=None, end: Optional[time]= None,d: Optional[date]= None) -> dict | None:
        event = self.get_event(event_id)
        if title:
            event["summary"] = title
        if start and end and d:
            if start >= end:
                raise Exception("start must be before end")
            event["start"] = {"dateTime": self._to_rfc3339(d,start), "timeZone": self.time_zone}
            event["end"] = {"dateTime": self._to_rfc3339(d,end), "timeZone": self.time_zone}

        return self.service.events().update(calendarId =self.calendar_id, eventId=event_id, body=event).execute()

    def create_calendar(self, title: str) -> dict:
        body = {"summary": title, "timeZone": self.time_zone
                }
        return self.service.calendars().insert(body=body).execute()


