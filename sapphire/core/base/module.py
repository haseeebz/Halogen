from abc import ABC
from types import MethodType
from typing import Tuple, Literal, Union
from .config import SapphireConfig
from collections.abc import Callable
from sapphire.core.base import SapphireEvents


class SapphireModule(ABC):

	def __init__(self, emit_event: Callable[[SapphireEvents.Event], None], config: SapphireConfig) -> None:
		super().__init__()
		self.eventbus_emit = emit_event
		self.config = config 
		self.has_commands = False


	@classmethod
	def name(cls) -> str:
		"""
		The name of the module. This is important for config file. By default, its the literal
		name of the class. 
		"""
		return cls.__name__
	

	def start(self) -> None:
		"""
		Function that is called once the core starts running. 
		It is recomended to put all of the setup here.
		Override this and do not call super().start()
		"""
		raise NotImplementedError(f"start method of class {self.__class__} not implemented.")


	def emit_event(self, event: SapphireEvents.Event) -> None:
		"""
		Internal function to call when the module wants to emit some event to the eventbus.
		"""
		if not isinstance(event, SapphireEvents.Event):
			log_event = SapphireEvents.LogEvent(
				self.name(),
				SapphireEvents.make_timestamp(),
				"warning",
				f"SapphireModule '{self.name()}' tried to emit an invalid event. " \
				"Expected argument was a Sapphire Event or its subclass. " \
				f"Got {type(event)}"
			)
			self.eventbus_emit(log_event)
			return
		
		self.eventbus_emit(event)


	def handled_events(self) -> list[type[SapphireEvents.Event]]:
		"""
		List of SapphireEvents that the module can handle. 
		These will be dispatched to the module via SapphireModule.handle(). 
		Override this and do not call super().handled_events()
		"""
		raise NotImplementedError(f"handled_events method of class {self.__class__} not implemented.")


	def handle(self, event: SapphireEvents.Event) -> None:
		"""
		The function called by SapphireCore to pass an event. 
		Override this and do not call super().handle()
		"""
		raise NotImplementedError(f"handle method of class {self.__class__} not implemented.")


	def log(
		self, 
		chain: SapphireEvents.Chain,
		level: Literal["debug", "info", "warning", "critical"],
		msg: str
	):
		"""
		Shorthand for creating a log event and emitting it to the bus.
		"""
		event = SapphireEvents.LogEvent(
			self.name(),
			SapphireEvents.make_timestamp(),
			chain,
			level,
			msg
		)
		self.emit_event(event)


	def define_command(
		self, 
		cmd: str, 
		func: Callable[[list[str], SapphireEvents.Chain], str], 
		info: str = ""
		):
		self.emit_event(
			SapphireEvents.CommandRegisterEvent(
				self.name(),
				SapphireEvents.make_timestamp(),
				SapphireEvents.chain(),
				self.name(),
				cmd,
				info,
				func
			)
		)


	def end(self) -> Tuple[bool, str]:
		"""
		Function called by SapphireCore to end the module. 
		The module must do all its clean up before returning True. 
		In case something goes wrong, return False + string. It will be logged. 
		Override this and do not call super().end()
		"""
		raise NotImplementedError(f"end method of class {self.__class__} not implemented.")