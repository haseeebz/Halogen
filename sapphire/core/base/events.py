from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Union
import threading

class SapphireEvents():

	_lock = threading.Lock()
	current_chain = 10000

	@classmethod
	def make_timestamp(cls):
		"Class method for giving a standard timestamp format for all events."
		return datetime.now().strftime("%H:%M:%S")
	
	@classmethod
	def chain(cls, event: Union["Event", None] = None):
		"Class Method to chain events using the chain_id. If empty, returns a new chain."
		if isinstance(event, SapphireEvents.Event):
			return event.chain_id
		else:
			chain = SapphireEvents.current_chain
			with cls._lock: SapphireEvents.current_chain += 1
			return chain
			
	@dataclass
	class Event():
		sender: str
		timestamp: str
		chain_id: int

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
		category: Literal["user", "confirmation"]
		message: str


	@dataclass
	class OutputEvent(Event):
		category: Literal["user", "confirmation", "error", "command", "greeting"]
		message: str
		final: bool


	@dataclass
	class CommandEvent(Event):
		cmd: str
		args: list[str]


	@dataclass
	class UserPromptEvent(Event):
		prompt: str


	@dataclass
	class AIResponseEvent(Event):
		message: str
		tasks: list[tuple[str, dict[str, str]]]



