from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class Event():
	sender: str
	timestamp: str


@dataclass
class LogEvent(Event):
	level: Literal["debug", "info", "warning", "critical"]
	message: str


@dataclass
class ShutdownEvent(Event):
	emergency: bool
	situation: Literal["request", "failure", "critical", "user"]


@dataclass
class InputEvent(Event):
	message: str


@dataclass
class OutputEvent(Event):
	message: str


@dataclass
class UserPromptEvent(Event):
	prompt: str


@dataclass
class AIResponseEvent(Event):
	message: str
	tasks: list[tuple[str, dict[str, str]]]



class SapphireEvents():

	@classmethod
	def make_timestamp(cls):
		"Class method for giving a standard timestamp format for all events."
		return datetime.now().strftime("%H:%M:%S")
	
	LogEvent = LogEvent
	ShutdownEvent = ShutdownEvent
