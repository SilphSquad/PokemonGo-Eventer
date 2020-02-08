#!/usr/bin/python3
import logging
import pathlib
import pickle

import yaml
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from Data.Attendee import Attendee
from Data.EventType import EventType

TOP_DIR = pathlib.Path(__file__).resolve().parent.parent
LOG_DIR = TOP_DIR.joinpath('logs')

LOGGER = logging.getLogger(__name__)

# If changing these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/spreadsheets.readonly']

config_file = TOP_DIR.joinpath('config.yaml')
if config_file.exists():
    with open(config_file, 'r', encoding='UTF-8') as config_yaml:
        CONFIG = yaml.safe_load(config_yaml) or {}
else:
    config_file.touch()
    with open(config_file, 'w', encoding='UTF-8') as config_yaml:
        CONFIG = {
            'Google Sheets ID': None,
            'Google Sheets Selection': None,
            'Google Calendar ID': None,
            'Ignored': []
        }
        yaml.safe_dump(CONFIG, config_yaml)


def get_creds():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if TOP_DIR.joinpath('token.pickle').exists():
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds
