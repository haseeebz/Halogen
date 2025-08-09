
import threading
from typing import Literal
from sapphire.base import SapphireEvents


class EventBus():

	def __init__(self) -> None:
		self.events: list[SapphireEvents.Event] = []
		self.lock = threading.Lock()

	def emit(self, event: SapphireEvents.Event):
		if not isinstance(event, SapphireEvents.Event):
			return
		with self.lock:
			self.events.append(event)

	def receive(self) -> SapphireEvents.Event:
		with self.lock:
			event = self.events.pop(0)
		return event
	
	def is_empty(self) -> bool:
		if len(self.events) > 0:
			return False
		else:
			return True
		
	def count(self) -> int:
		return len(self.events)
	
	def get_all_queued(self) -> list[SapphireEvents.Event]:
		return self.events
