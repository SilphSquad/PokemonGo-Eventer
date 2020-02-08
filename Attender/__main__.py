#!/usr/bin/python3
import logging

import yaml
from googleapiclient.discovery import build

from Attender import init_logger
from Data import EventType, CONFIG, get_creds

LOGGER = logging.getLogger(__name__)


def main():
    service = build('sheets', 'v4', credentials=get_creds(), cache_discovery=False)

    current_sheets = list_sheets(service=service)
    with open('attendees.yaml', 'w', encoding='UTF-8') as attendee_file:
        attendees = []
        for entry in current_sheets[1:]:
            if entry[0].strip() in CONFIG['Ignored']:
                continue
            LOGGER.info(f"Entry: {entry}")
            types = []
            for temp in entry[2].split(','):
                temp = temp.strip()
                if temp == "General Events" or temp == "Events" or temp == "General Event":
                    types.append(EventType.GENERAL_EVENT)
                elif temp == "Giovanni" or temp == "Giovanni Special Research":
                    types.append(EventType.GIOVANNI_SPECIAL_RESEARCH)
                elif temp == "Research Breakthrough":
                    types.append(EventType.RESEARCH_BREAKTHROUGH)
                elif temp == "Raid Boss" or temp == "Raid Battle":
                    types.append(EventType.RAID_BATTLE)
                elif temp == "Community Day":
                    types.append(EventType.COMMUNITY_DAY)
                elif temp == "Raid Hour":
                    types.append(EventType.RAID_HOUR)
                elif temp == "Raid Day":
                    types.append(EventType.RAID_DAY)
                elif temp == "GO Battle League":
                    types.append(EventType.GO_BATTLE_LEAGUE)
                else:
                    LOGGER.error(f"Unknown Event Type: `{temp}`")
            entry_obj = {'email': entry[1].strip(), 'name': entry[0].strip(), 'types': [x.name for x in types]}
            attendees.append(entry_obj)
        yaml.safe_dump(attendees, attendee_file)


def list_sheets(service):
    results = service.spreadsheets().values().get(spreadsheetId=CONFIG['Google Sheets ID'],
                                                  range=CONFIG['Google Sheets Selection']).execute()
    return results.get('values', [])


if __name__ == '__main__':
    init_logger()
    main()
