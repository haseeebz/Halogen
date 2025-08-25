from collections.abc import Callable
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import time

from halogen.base import HalogenEvents, HalogenModule, HalogenConfig
from halogen.modules.tasks.base import HalogenTask, HalogenTaskError

class Chrono(HalogenModule):

	def __init__(self, emit_event: Callable[[HalogenEvents.Event], None], config: HalogenConfig) -> None:
		super().__init__(emit_event, config)
		self.has_tasks = True
		self.executor = ThreadPoolExecutor()
	
	@classmethod
	def name(cls):
		return "chrono"

	@classmethod
	def info(cls):
		return "Module for time and reminders related functionality."
	

	def handled_events(self) -> list[type[HalogenEvents.Event]]:
		return []
	

	def start(self) -> None:
		pass


	def end(self) -> tuple[bool, str]:
		self.executor.shutdown(False, True)
		return (True, "Shutdown the ThreadPool and killed all timers.")


	@HalogenTask(
		"set_duration_timer", 
		"Set a time (in integar seconds) based reminder. Add context to the message also.",
		["message:str", "seconds:int"]
		)
	def set_duration_timer(self, chain: HalogenEvents.Chain, msg: str, sec: str):

		if not sec.isdigit():
			raise HalogenTaskError(f"{sec} is not a valid integar.")

		sec = int(sec)

		def timer():
			time.sleep(sec)
			
			ev = HalogenEvents.NotifyEvent(
				self.name(),
				HalogenEvents.make_timestamp(),
				chain,
				f"Timer Finished. Tell the user. Reminder: {msg}"
			)

			self.emit_event(ev)

		self.executor.submit(timer)

		return f"Set reminder to notify after {sec}s."


