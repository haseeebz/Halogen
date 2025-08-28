import threading
from typing import Literal
from halogen.base import HalogenEvents
from queue import Queue, Empty


class EventBus():

	def __init__(self) -> None:
		self.events: Queue[HalogenEvents.Event] = Queue()
		self.lock = threading.Lock()
		self._count = 0 


	def emit(self, event: HalogenEvents.Event):
		if isinstance(event, HalogenEvents.Event):
			self.events.put(event)
			with self.lock: self._count += 1


	def receive(self, timeout: int) -> HalogenEvents.Event | None:
		try:
			event = self.events.get(True, timeout)
			with self.lock: self._count -= 1
		except Empty:
			event = None

		return event


	def count(self) -> int: 
		return self._count
	

	def empty(self) -> bool:
		if self._count > 0:
			return False
		return True
