
import threading
from .events import Event


class EventBus():

	def __init__(self) -> None:
		self.events: list[Event] = []
		self.lock = threading.Lock()

	def emit(self, event: Event):
		with self.lock:
			self.events.append(event)

	def receive(self) -> Event:
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