#!/usr/bin/python3
import logging
from typing import List

from Eventer.EventType import EventType

LOGGER = logging.getLogger(__name__)


class Attendee:
	def __init__(self, name: str, email: str, event_types: List[EventType]):
		self.name = name
		self.email = email
		self.event_types = event_types

	def output(self):
		return {'displayName': self.name, 'email': self.email, 'optional': True}

	def __str__(self) -> str:
		output = 'Attendee('
		for key, value in self.__dict__.items():
			output += f"{key}={value}, "
		return output[:-2] + ')'
