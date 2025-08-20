from collections.abc import Callable

from halogen.base import HalogenEvents, HalogenModule, HalogenConfig
from halogen.modules.tasks.base import HalogenTask, HalogenTaskError

class Chrono(HalogenModule):

	def __init__(self, emit_event: Callable[[HalogenEvents.Event], None], config: HalogenConfig) -> None:
		super().__init__(emit_event, config)
		self.has_tasks = True

	
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


	def end(self) -> Tuple[bool, str]:
		return (True, "No specific end action needed.")


