from abc import ABC
from .events import Event
from collections.abc import Callable


class SapphireModule(ABC):

	def __init__(self, emit_event: Callable[[Event], None]) -> None:
		super().__init__()
		self.eventbus_emit = emit_event


	def name(self) -> None:
		"""
		The name of the module. This is important for config files.
		Override this.
		"""
		raise NotImplementedError()
	

	def start(self) -> None:
		"""
		Function that is called once the core starts running. 
		It is recomended to put all of the setup here.
		Override this and do not call super().start()
		"""
		raise NotImplementedError()


	def emit_event(self, event: Event) -> None:
		"""
		Internal function to call when the module wants to emit some event to the eventbus.
		"""
		self.eventbus_emit(event)


	def handled_events(self) -> list[type[Event]]:
		"""
		List of SapphireEvents that the module can handle. 
		These will be dispatched to the module via SapphireModule.handle(). 
		Override this and do not call super().handled_events()
		"""
		raise NotImplementedError()


	def handle(self, event: Event) -> None:
		"""
		The function called by SapphireCore to pass an event. 
		Override this and do not call super().handle()
		"""
		raise NotImplementedError()


	def end(self) -> bool:
		"""
		Function called by SapphireCore to end the module. 
		The module must do all its clean up before returning True. 
		In case something goes wrong, return False. It will be logged. 
		Override this and do not call super().end()
		"""
		raise NotImplementedError()