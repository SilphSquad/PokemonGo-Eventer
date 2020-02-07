#!/usr/bin/python3
import logging
from typing import Dict, Any

from Data.EventType import EventType

LOGGER = logging.getLogger(__name__)


class Attendee:
    def __init__(self, entry: Dict[str, Any]):
        self.name = entry['name']
        self.email = entry['email']
        self.event_types = [EventType[x] for x in entry['types']]

    def output(self):
        return {'displayName': self.name, 'email': self.email, 'optional': True}

    def __str__(self) -> str:
        output = 'Attendee('
        for key, value in self.__dict__.items():
            output += f"{key}={value}, "
        return output[:-2] + ')'
