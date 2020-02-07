#!/usr/bin/python3
import logging
from datetime import datetime
from typing import Optional, List, Dict

from pytz import timezone

from Data.EventType import EventType

LOGGER = logging.getLogger(__name__)


class Event:
    def __init__(self, name: str, event_type: EventType, start_time: str, end_time: str, timezone: Optional[str] = None,
                 wild: Optional[List[str]] = None, research: Optional[List[str]] = None,
                 eggs: Optional[Dict[str, List[str]]] = None, raids: Optional[Dict[str, List[str]]] = None,
                 bonuses: Optional[List[str]] = None):
        self.name = name
        self.event_type = event_type
        self.timezone = timezone or 'Pacific/Auckland'
        self.start_time = start_time
        self.end_time = end_time
        self.wild = wild or []
        self.research = research or []
        self.eggs = eggs or {}
        self.raids = raids or {}
        self.bonuses = bonuses or []

    def local_time(self) -> str:
        return timezone(self.timezone) \
            .localize(datetime.strptime(self.start_time, '%Y-%m-%dT%H:%M:%S')) \
            .astimezone(timezone('Pacific/Auckland')) \
            .isoformat(sep='T')

    def description(self) -> str:
        output = ''
        if self.wild:
            output += 'Wild:\n'
            output += '    - ' + ('\n    - '.join(self.wild)) + '\n'
        if self.research:
            output += 'Research:\n'
            output += '    - ' + ('\n    - '.join(self.research)) + '\n'
        if self.eggs:
            output += 'Eggs:\n'
            for (key, values) in self.eggs.items():
                output += f"    {key}:"
                output += '\n        - ' + ('\n        - '.join(values)) + '\n'
        if self.raids:
            output += 'Raids:\n'
            for (key, values) in self.raids.items():
                output += f"    {key}:\n"
                output += '        - ' + ('\n        - '.join(values)) + '\n'
        if self.bonuses:
            output += 'Other:\n'
            output += '    - ' + ('\n    - '.join(self.bonuses)) + '\n'
        return output.strip()

    def __str__(self) -> str:
        output = 'Event('
        for key, value in self.__dict__.items():
            output += f"{key}={value}, "
        return output[:-2] + ')'
