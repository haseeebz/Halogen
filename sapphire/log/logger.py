from collections.abc import Callable
from sapphire.core.base import SapphireModule, SaphhireEvent, Event


class Logger(SapphireModule):

	def __init__(self, emit_event: Callable[[Event], None]) -> None:
		super().__init__(emit_event)

	def handled_events(self) -> list[type[Event]]:
		return [
			SaphhireEvent.LogEvent
		]
	
	def handle(self, event: Event) -> None:
		match event:
			case SaphhireEvent.LogEvent():
				self.log(event)

	def log(self, event: SaphhireEvent.LogEvent) -> None:

		log_str = f"[{event.timestamp}] [{event.level.upper()}] ({event.sender.capitalize()}) {event.message}\n"

		with open("saph.log", "a+") as file:
			file.write(log_str)

			
