#!/usr/bin/python3
import logging
from argparse import ArgumentParser, Namespace
from datetime import datetime

import yaml
from googleapiclient import errors
from googleapiclient.discovery import build

from Data import EventType, Attendee, CONFIG, get_creds
from Eventer import init_logger, Event, TOP_DIR

LOGGER = logging.getLogger(__name__)


def get_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('-t', '--test', action='store_true')
    return parser.parse_args()


args = get_arguments()

if args.test:
    ATTENDEES = []
else:
    with open('attendees.yaml', 'r', encoding='UTF-8') as attendee_file:
        temp = yaml.safe_load(attendee_file)
        ATTENDEES = [Attendee(entry=entry) for entry in temp if entry['name'] != 'Macro303']


def get_start_date() -> datetime:
    today = datetime.today()
    month = today.month - 1
    year = today.year if month < today.month else today.year - 1
    return datetime.today().replace(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)


def main():
    service = build('calendar', 'v3', credentials=get_creds(), cache_discovery=False)

    current_events = list_events(service=service)

    LOGGER.info(f"Existing Events: {[x['start']['dateTime'] + '-' + x['summary'] for x in current_events]}")
    files = [p for p in TOP_DIR.joinpath("events").iterdir() if p.is_file()]
    for file in files:
        with open(file, 'r', encoding='UTF-8') as event_file:
            yaml_event = yaml.safe_load(event_file)
            event_type = EventType[yaml_event['Type']]
            dif = get_start_date() - datetime.strptime(yaml_event['EndTime'], '%Y-%m-%dT%H:%M:%S')
            if dif.days > 1:
                LOGGER.warning(f"Skipping Old Event `{yaml_event['Name']}` => {dif}")
            else:
                if event_type in [EventType.GIOVANNI_SPECIAL_RESEARCH, EventType.RESEARCH_BREAKTHROUGH,
                                  EventType.RAID_BATTLE, EventType.GO_BATTLE_LEAGUE]:
                    start = Event(
                        name=yaml_event['Name'] + ' Start',
                        event_type=event_type,
                        start_time=yaml_event['StartTime'],
                        end_time=yaml_event['StartTime'],
                        timezone=yaml_event['Timezone'],
                        wild=yaml_event['Wild'],
                        research=yaml_event['Research'],
                        eggs=yaml_event['Eggs'],
                        raids=yaml_event['Raids'],
                        bonuses=yaml_event['Bonus']
                    )
                    results = filter(
                        lambda x: x['summary'] == start.name and x['start']['dateTime'] == start.local_time(),
                        current_events)
                    result = next(results, None)
                    if result:
                        LOGGER.info(f"{start.name} already exists, updating")
                        update_event(service=service, file_event=start, cal_event=result)
                    else:
                        create_event(service=service, file_event=start)
                    end = Event(
                        name=yaml_event['Name'] + ' End',
                        event_type=event_type,
                        start_time=yaml_event['EndTime'],
                        end_time=yaml_event['EndTime'],
                        timezone=yaml_event['Timezone'],
                        wild=yaml_event['Wild'],
                        research=yaml_event['Research'],
                        eggs=yaml_event['Eggs'],
                        raids=yaml_event['Raids'],
                        bonuses=yaml_event['Bonus']
                    )
                    results = filter(lambda x: x['summary'] == end.name and x['start']['dateTime'] == end.local_time(),
                                     current_events)
                    result = next(results, None)
                    if result:
                        LOGGER.info(f"{end.name} already exists, updating")
                        update_event(service=service, file_event=end, cal_event=result)
                    else:
                        create_event(service=service, file_event=end)
                else:
                    event = Event(
                        name=yaml_event['Name'],
                        event_type=event_type,
                        start_time=yaml_event['StartTime'],
                        end_time=yaml_event['EndTime'],
                        timezone=yaml_event['Timezone'],
                        wild=yaml_event['Wild'],
                        research=yaml_event['Research'],
                        eggs=yaml_event['Eggs'],
                        raids=yaml_event['Raids'],
                        bonuses=yaml_event['Bonus']
                    )
                    results = filter(
                        lambda x: x['summary'] == event.name and x['start']['dateTime'] == event.local_time(),
                        current_events)
                    result = next(results, None)
                    if result:
                        LOGGER.info(f"{event.name} already exists, updating")
                        update_event(service=service, file_event=event, cal_event=result)
                    else:
                        create_event(service=service, file_event=event)


def update_event(service, file_event, cal_event):
    if file_event.description() != (cal_event.get('description', '')):
        print("---")
        print(file_event.description())
        print("---")
    event_attendees = [x for x in ATTENDEES if file_event.event_type in x.event_types]
    current_attendees = [x['email'] for x in cal_event.get('attendees', [])]
    missing = [x for x in event_attendees if x.email not in set(current_attendees)]
    if missing:
        cal_event['attendees'] = [x.output() for x in event_attendees]
        service.events().patch(calendarId=CONFIG['Google Calendar ID'], eventId=cal_event['id'],
                               body=cal_event).execute()
    else:
        LOGGER.info("No update necessary")


def list_events(service):
    # Call the Calendar API
    start = get_start_date().isoformat() + 'Z'
    LOGGER.info(f"Getting all the events from {start}")
    events_result = service.events().list(calendarId=CONFIG['Google Calendar ID'], timeMin=start, singleEvents=True,
                                          orderBy='startTime').execute()
    return events_result.get('items', [])


def create_event(service, file_event):
    event_json = {
        'summary': file_event.name,
        'description': file_event.description(),
        'start': {
            'dateTime': file_event.start_time,
            'timeZone': file_event.timezone
        },
        'end': {
            'dateTime': file_event.end_time,
            'timeZone': file_event.timezone
        },
        'attendees': [x.output() for x in ATTENDEES if file_event.event_type in x.event_types],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 2 * 60},
                {'method': 'popup', 'minutes': 24 * 60}
            ]
        },
        'guestsCanSeeOtherGuests': False,
        'guestsCanModify': False,
        'transparency': 'transparent'
    }

    try:
        calendar_event = service.events().insert(calendarId=CONFIG['Google Calendar ID'], body=event_json).execute()
        LOGGER.info(f"{file_event.name} Event created: {calendar_event.get('htmlLink')}")
    except errors.HttpError as err:
        LOGGER.error(err)


if __name__ == '__main__':
    init_logger()
    main()
