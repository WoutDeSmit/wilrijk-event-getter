import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


class CalendarAdder:
    def __init__(self):
        self.creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

    def create_event(self,
                     start_time: datetime.datetime,
                     end_time: datetime.datetime,
                     summary: str,
                     description: str) -> None:
        try:
            service = build("calendar", "v3", credentials=self.creds)

            # Call the Calendar API
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': str(start_time).replace(" ", "T")+"+01:00",
                },
                'end': {
                    'dateTime': str(end_time).replace(" ", "T")+"+01:00",
                },
            }

            service.events().insert(calendarId='primary', body=event).execute()
            print(f"Event {summary} with description {description} created.")

        except HttpError as error:
            print(f"An error occurred: {error}")

    def get_events(self) -> list:
        try:
            service = build("calendar", "v3", credentials=self.creds)

            # Call the Calendar API
            now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
            events_result = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=now,
                    maxResults=100,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])

            if not events:
                print("No upcoming events found.")
                return []

            return events

        except HttpError as error:
            print(f"An error occurred: {error}")
