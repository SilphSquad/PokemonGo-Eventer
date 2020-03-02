#!/usr/bin/python3
import logging
from argparse import ArgumentParser, Namespace
from datetime import datetime
from typing import List

import yaml
from googleapiclient import errors
from googleapiclient.discovery import build

from Eventer import init_logger, Event, TOP_DIR, Attendee, get_creds, CONFIG, EventType

LOGGER = logging.getLogger(__name__)


def get_arguments() -> Namespace:
	parser = ArgumentParser()
	parser.add_argument('-t', '--test', action='store_true')
	return parser.parse_args()


args = get_arguments()


def parse_attendees() -> List[Attendee]:
	service = build('sheets', 'v4', credentials=get_creds(), cache_discovery=False)

	current_sheets = list_sheets(service=service)
	attendees = []
	for entry in current_sheets[1:]:
		if entry[0].strip() in CONFIG['Ignored']:
			continue
		LOGGER.info(f"Entry: {entry}")
		event_types = []
		for temp in entry[2].split(','):
			temp = temp.strip()
			if temp in ['General Events', 'Events', 'General Event']:
				event_types.append(EventType.GENERAL_EVENTS)
			elif temp in ['GO Battle League']:
				event_types.append(EventType.GO_BATTLE_LEAGUE)
			elif temp in ['Raid Boss', 'Raid Battle', 'Raid Battles']:
				event_types.append(EventType.RAID_BATTLES)
			elif temp in ['Giovanni Special Research']:
				event_types.append(EventType.GIOVANNI_SPECIAL_RESEARCH)
			elif temp in ['Research Breakthrough']:
				event_types.append(EventType.RESEARCH_BREAKTHROUGH)
			elif temp in ['Raid Day']:
				event_types.append(EventType.RAID_DAY)
			elif temp in ['Community Day']:
				event_types.append(EventType.COMMUNITY_DAY)
			elif temp in ['Raid Hour']:
				event_types.append(EventType.RAID_HOUR)
			elif temp in ['Pokemon Spotlight Hour']:
				event_types.append(EventType.POKEMON_SPOTLIGHT_HOUR)
			elif temp in ['Mystery Bonus Hour']:
				event_types.append(EventType.MYSTERY_BONUS_HOUR)
			else:
				LOGGER.error(f"Unknown Event Type: `{temp}`")
		attendees.append(Attendee(
			email=entry[1].strip(),
			name=entry[0].strip(),
			event_types=event_types
		))
	return attendees


def list_sheets(service):
	results = service.spreadsheets().values().get(spreadsheetId=CONFIG['Google Sheets ID'],
	                                              range=CONFIG['Google Sheets Selection']).execute()
	return results.get('values', [])


def get_start_date() -> datetime:
	today = datetime.today()
	month = today.month - 2
	year = today.year if month < today.month else today.year - 1
	return datetime.today().replace(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)


def main():
	attendees = parse_attendees()
	parse_events(attendees=attendees)


def parse_events(attendees: List[Attendee]):
	service = build('calendar', 'v3', credentials=get_creds(), cache_discovery=False)

	current_events = list_events(service=service)

	LOGGER.info(f"Existing Events: {[x['start']['dateTime'] + '-' + x['summary'] for x in current_events]}")
	files = [p for p in TOP_DIR.joinpath("events").iterdir() if p.is_file()]
	for file in files:
		with open(file, 'r', encoding='UTF-8') as event_file:
			yaml_event = yaml.safe_load(event_file)
			event_type = EventType[yaml_event['Type']]
			dif = datetime.today() - datetime.strptime(yaml_event['EndTime'], '%Y-%m-%dT%H:%M:%S')
			LOGGER.debug(f"{yaml_event['Name']} Age: {dif.days}")
			if dif.days > 14:
				LOGGER.warning(
					f"Skipping Old Event `{yaml_event['StartTime'].split('T')[0]}|{yaml_event['Name']}` => {dif.days} days old")
			else:
				start_time = datetime.strptime(yaml_event['StartTime'], '%Y-%m-%dT%H:%M:%S')
				end_time = datetime.strptime(yaml_event['EndTime'], '%Y-%m-%dT%H:%M:%S')
				if (end_time - start_time).days > 10:
					start = Event(
						name=yaml_event['Name'] + ' Start',
						event_type=event_type,
						start_time=yaml_event['StartTime'],
						end_time=yaml_event['StartTime'],
						time_zone=yaml_event['Timezone'],
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
						update_event(service=service, file_event=start, cal_event=result,
						             attendees=[x for x in attendees if start.event_type in x.event_types])
					else:
						create_event(service=service, file_event=start,
						             attendees=[x for x in attendees if start.event_type in x.event_types])
					end = Event(
						name=yaml_event['Name'] + ' End',
						event_type=event_type,
						start_time=yaml_event['EndTime'],
						end_time=yaml_event['EndTime'],
						time_zone=yaml_event['Timezone'],
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
						update_event(service=service, file_event=end, cal_event=result,
						             attendees=[x for x in attendees if end.event_type in x.event_types])
					else:
						create_event(service=service, file_event=end,
						             attendees=[x for x in attendees if end.event_type in x.event_types])
				else:
					event = Event(
						name=yaml_event['Name'],
						event_type=event_type,
						start_time=yaml_event['StartTime'],
						end_time=yaml_event['EndTime'],
						time_zone=yaml_event['Timezone'],
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
						update_event(service=service, file_event=event, cal_event=result,
						             attendees=[x for x in attendees if event.event_type in x.event_types])
					else:
						create_event(service=service, file_event=event,
						             attendees=[x for x in attendees if event.event_type in x.event_types])


def update_event(service, file_event: Event, cal_event, attendees: List[Attendee]):
	updated = False
	if file_event.description() != (cal_event.get('description', '')):
		print("---")
		print(file_event.description())
		print("---")
		updated = True
	current_attendees = [x['email'] for x in cal_event.get('attendees', [])]
	missing = [x for x in attendees if x.email not in set(current_attendees)]
	if missing:
		cal_event['attendees'] = [x.output() for x in attendees]
		if not args.test:
			service.events().patch(calendarId=CONFIG['Google Calendar ID'], eventId=cal_event['id'],
			                       body=cal_event).execute()
		LOGGER.info(f"{file_event.start_time.split('T')[0]}|{file_event.name} Event updated")
	elif not updated:
		LOGGER.info(f"No update for {file_event.start_time.split('T')[0]}|{file_event.name}")


def list_events(service):
	# Call the Calendar API
	start = get_start_date().isoformat() + 'Z'
	LOGGER.info(f"Getting all the events from {start}")
	events_result = service.events().list(calendarId=CONFIG['Google Calendar ID'], timeMin=start, singleEvents=True,
	                                      orderBy='startTime').execute()
	return events_result.get('items', [])


def create_event(service, file_event: Event, attendees: List[Attendee]):
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
		'attendees': [x.output() for x in attendees],
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
		if not args.test:
			calendar_event = service.events().insert(calendarId=CONFIG['Google Calendar ID'], body=event_json).execute()
		LOGGER.info(f"{file_event.start_time.split('T')[0]}|{file_event.name} Event created")
	except errors.HttpError as err:
		LOGGER.error(err)


if __name__ == '__main__':
	init_logger()
	main()
