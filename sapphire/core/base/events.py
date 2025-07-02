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
	urgency: Literal["request", "failure", "critical"]

class SapphireEvents():

	@classmethod
	def make_timestamp(cls):
		"Class method for giving a standard timestamp format for all events."
		return datetime.now().strftime("%d/%m/%y : %H:%M:%S")
	
	LogEvent = LogEvent
	ShutdownEvent = ShutdownEvent
