#!/usr/bin/python3
import logging
from enum import Enum, auto

LOGGER = logging.getLogger(__name__)


class EventType(Enum):
    GENERAL_EVENT = auto()
    GO_BATTLE_LEAGUE = auto()
    RAID_BATTLE = auto()
    GIOVANNI_SPECIAL_RESEARCH = auto()
    RESEARCH_BREAKTHROUGH = auto()
    RAID_DAY = auto()
    COMMUNITY_DAY = auto()

    RAID_HOUR = auto()
    SPOTLIGHT_HOUR = auto()
    MYSTERY_BONUS = auto()
