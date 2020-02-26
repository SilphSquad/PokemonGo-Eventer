#!/usr/bin/python3
import logging
import pathlib

from Eventer.Event import Event

TOP_DIR = pathlib.Path(__file__).resolve().parent.parent
LOG_DIR = TOP_DIR.joinpath('logs')

LOGGER = logging.getLogger(__name__)


def init_logger() -> None:
	LOG_DIR.mkdir(exist_ok=True)
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	file = logging.FileHandler(filename=LOG_DIR.joinpath('Eventer.log'), encoding='utf-8')
	file.setLevel(logging.DEBUG)
	logging.basicConfig(
		level=logging.DEBUG,
		format='[%(asctime)s] [%(levelname)-8s] {%(name)s} | %(message)s',
		handlers=[
			console,
			file
		]
	)
