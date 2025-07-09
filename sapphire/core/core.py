import time, shlex
from pathlib import Path
from typing import Callable, MutableSequence, Literal
from .base import (
	EventBus, 
	SapphireModule, 
	SapphireConfig, 
	SapphireEvents,
	SapphireModuleManager,
	SapphireCommands
)


class SapphireCore():

	def __init__(self, root: str) -> None:

		self.root = Path(root).resolve().parent
		self.config: SapphireConfig = SapphireConfig()
		
		self.eventbus: EventBus = EventBus()
		
		self.log(
			SapphireEvents.chain(), 
			"info", 
			f"Hello {self.config.get("user.name", "User")} :D"
		)

		self.manager = SapphireModuleManager(self.root, self.config, self.eventbus.emit)
		self.manager.load_modules()

		self.command = SapphireCommands(self.eventbus.emit)
		self.define_core_commands()

		self.core_events: MutableSequence[type[SapphireEvents.Event]] = [
			SapphireEvents.ShutdownEvent,
			SapphireEvents.CommandEvent
		]

		self.is_running: bool = True
		self.shutdown_requested = False

		

		
	def run(self):
		
		self.manager.start_modules()
		
		while self.is_running: #main loop

			if self.eventbus.is_empty():
				if self.shutdown_requested: #shutdown once the bus is empty
					self.shutdown()
					break
				time.sleep(0.05)
				continue
			
			event = self.eventbus.receive() #non-blocking but we checked for bus' payload above
			event_type = type(event)

			# passing events

			if event_type in self.core_events: 
				self.handle(event)

			if event_type not in self.manager.defined_events():
				continue

			for module in self.manager.get_module_list(event_type):
				try:
					module.handle(event) 
				except Exception as e:
					self.log(
						SapphireEvents.chain(),
						"critical",
						f"Module '{module.name()}' could not handle an event! " \
						f"Event = {event}. Encountered Error = {e.__class__.__name__}:{e}"
					)


	def handle(self, event: SapphireEvents.Event):
		match event:
			case SapphireEvents.ShutdownEvent():
				if event.emergency:
					self.shutdown() 
					return
				self.shutdown_requested = True
			case SapphireEvents.CommandEvent():
				self.command.interpret(event)


	def log(self, chain: SapphireEvents.Chain, level: Literal["debug", "info", "warning", "critical"], msg: str):
		event = SapphireEvents.LogEvent(
			"core",
			SapphireEvents.make_timestamp(),
			chain,
			level,
			msg
		)
		self.eventbus.emit(event)


	def shutdown(self):
		self.is_running = False
		logger = self.manager.end_modules()
		
		if not logger: return

		for event in self.eventbus.get_all_queued():
			if isinstance(event, SapphireEvents.LogEvent):
				logger.handle(event)

		event = SapphireEvents.LogEvent(
			"core",
			SapphireEvents.make_timestamp(),
			SapphireEvents.chain(),
			"info",
			"Sapphire is now shutting down."
		)

		logger.handle(event)
		logger.end()


	def define_core_commands(self):
		self.command.define(
			self.shutdown_command,
			"shutdown",
			"Request Sapphire to shutdown. Args: []"
		)

		self.command.define(
			self.get_command,
			"get",
			"Get internal values from Sapphire. Use 'get help' to see the accessible terms."
		)


	def shutdown_command(self, args: list[str], chain: SapphireEvents.Chain) -> str:
		
		self.log(
			chain,
			"info",
			f"Client with chain id {chain} requested sapphire to shutdown."
		)

		event = SapphireEvents.ShutdownEvent(
			"core",
			SapphireEvents.make_timestamp(),
			chain,
			False,
			"user"
		)
		self.eventbus.emit(event)

		return "Requested Sapphire to shutdown."
	

	_get_terms = {}
	def get_command(self, args: list[str], chain: SapphireEvents.Chain) -> str:

		if not self._get_terms:
			self._get_terms = {
				"chain" : lambda: SapphireEvents._intern_chain.__str__(),
				"user" : lambda: self.config.get("user.name", "Unknown"),
				"help" : lambda: f"Accessible terms: {[x for x in self._get_terms.keys()]}"
			}


		num_args = len(args)
		if num_args != 1:
			value = self._get_terms["help"]()
			return value
		
		item = args[0]
		value = self._get_terms.get(item, "help")()
		return value

