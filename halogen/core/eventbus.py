
import threading
from typing import Literal
from halogen.base import HalogenEvents


class EventBus():

	def __init__(self) -> None:
		self.events: list[HalogenEvents.Event] = []
		self.lock = threading.Lock()

	def emit(self, event: HalogenEvents.Event):
		if not isinstance(event, HalogenEvents.Event):
			return
		with self.lock:
			self.events.append(event)

	def receive(self) -> HalogenEvents.Event:
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
	
	def get_all_queued(self) -> list[HalogenEvents.Event]:
		return self.events
