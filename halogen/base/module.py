from abc import ABC
from types import MethodType
from typing import Tuple, Literal, Union
from collections.abc import Callable

from .events import HalogenEvents
from .config import HalogenConfig
from .chain import Chain


class HalogenModule(ABC):

	def __init__(self, emit_event: Callable[[HalogenEvents.Event], None], config: HalogenConfig) -> None:
		super().__init__()
		self.eventbus_emit = emit_event
		self.config = config 
		self.has_commands = False
		self.has_tasks = False


	@classmethod
	def name(cls) -> str:
		"""
		The name of the module. This is important for config file. By default, its the literal
		name of the class. 
		"""
		return cls.__name__
	

	@classmethod
	def info(cls) -> str:
		"""
		The info and details related to the module. 
		"""
		return f"No information provided for {cls.name()}"


	def start(self) -> None:
		"""
		Function that is called once the core starts running. 
		It is recomended to put all of the setup here.
		Override this and do not call super().start()
		"""
		raise NotImplementedError(f"start method of class {self.__class__} not implemented.")


	def emit_event(self, event: HalogenEvents.Event) -> None:
		"""
		Internal function to call when the module wants to emit some event to the eventbus.
		"""
		if not isinstance(event, HalogenEvents.Event):
			log_event = HalogenEvents.LogEvent(
				self.name(),
				HalogenEvents.make_timestamp(),
				"warning",
				f"HalogenModule '{self.name()}' tried to emit an invalid event. " \
				"Expected argument was a Halogen Event or its subclass. " \
				f"Got {type(event)}"
			)
			self.eventbus_emit(log_event)
			return
		
		self.eventbus_emit(event)


	def handled_events(self) -> list[type[HalogenEvents.Event]]:
		"""
		List of HalogenEvents that the module can handle. 
		These will be dispatched to the module via HalogenModule.handle(). 
		Override this and do not call super().handled_events()
		"""
		raise NotImplementedError(f"handled_events method of class {self.__class__} not implemented.")


	def handle(self, event: HalogenEvents.Event) -> None:
		"""
		The function called by HalogenCore to pass an event. 
		Override this and do not call super().handle()
		"""
		raise NotImplementedError(f"handle method of class {self.__class__} not implemented.")


	def log(
		self, 
		chain: Chain,
		level: Literal["debug", "info", "warning", "critical"],
		msg: str
	):
		"""
		Shorthand for creating a log event and emitting it to the bus.
		"""
		event = HalogenEvents.LogEvent(
			self.name(),
			HalogenEvents.make_timestamp(),
			chain,
			level,
			msg
		)
		self.emit_event(event)


	def define_command(
		self, 
		cmd: str, 
		func: Callable[[list[str], Chain], str], 
		info: str = ""
		):
		self.emit_event(
			HalogenEvents.CommandRegisterEvent(
				self.name(),
				HalogenEvents.make_timestamp(),
				HalogenEvents.chain(),
				self.name(),
				cmd,
				info,
				func
			)
		)


	def end(self) -> Tuple[bool, str]:
		"""
		Function called by HalogenCore to end the module. 
		The module must do all its clean up before returning True. 
		In case something goes wrong, return False + string. It will be logged. 
		Override this and do not call super().end()
		"""
		raise NotImplementedError(f"end method of class {self.__class__} not implemented.")