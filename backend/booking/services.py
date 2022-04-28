from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings


SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    credentials = service_account.Credentials.from_service_account_info(
        settings.SERVICE_SECRETS, scopes=SCOPES
    )
    return build("calendar", "v3", credentials=credentials)
