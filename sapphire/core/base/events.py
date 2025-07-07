from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Union
import threading

class SapphireEvents():

	_lock = threading.Lock()
	
	@dataclass(frozen = True)
	class Chain():
		context: int
		flow: int

		def __str__(self) -> str:
			return f"({self.context}:{self.flow})"
		
		def __eq__(self, other) -> bool:
			return (self.context, self.flow) == (other.context, other.flow)
		
		
		

	_intern_chain = Chain(0, 0)
	_current_context = 0

	@classmethod
	def chain(cls, event: Union["Event", None] = None) -> Chain:
		"Class Method to chain events. If empty, returns a new chain."
		if isinstance(event, cls.Event):
			return event.chain
		else:
			chain = cls._intern_chain
			with cls._lock: 
				cls._intern_chain = cls.Chain(
					0,
					chain.flow + 1
				)
			return chain
		
		
	@classmethod
	def new_context_chain(cls) -> Chain:
		"Method for getting a chain with a new context."
		with cls._lock: cls._current_context += 1
		chain = cls.Chain(
			cls._current_context, 0
		)
		return chain
	

	@classmethod
	def make_timestamp(cls):
		"Class method for giving a standard timestamp format for all events."
		return datetime.now().strftime("%H:%M:%S")
		
			
	@dataclass
	class Event():
		sender: str
		timestamp: str
		chain: "SapphireEvents.Chain"

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
		category: Literal["user", "confirmation", "command"]
		message: str


	@dataclass
	class OutputEvent(Event):
		category: Literal["user", "confirmation", "command", "error", "greeting"]
		message: str


	@dataclass
	class PromptEvent(Event):
		prompt: str

	@dataclass
	class AIResponseEvent(Event):
		message: dict[str, str]
		tasks: list[tuple[str, dict[str, str]]]



