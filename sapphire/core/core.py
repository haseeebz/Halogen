import time, os
from pathlib import Path
from typing import Callable, MutableSequence, Literal

from sapphire.base import (
	SapphireModule, 
	SapphireConfig,
	SapphireConfigLoader,
	SapphireEvents
)

from .eventbus import EventBus
from .manager import SapphireModuleManager



class SapphireCore():

	def __init__(self) -> None:

		self.config: SapphireConfig = SapphireConfigLoader().load()

		self.is_running: bool = True


		#self.event_logs = self.root / "events.log"


		self.core_events: MutableSequence[type[SapphireEvents.Event]] = [
			SapphireEvents.ShutdownEvent,
		]
		
		self.eventbus: EventBus = EventBus()
		
		self.log(
			SapphireEvents.chain(), 
			"info", 
			f"Hello {self.config.get('user.name', 'User')} :D"
		)

		self.manager = SapphireModuleManager(self.config, self.eventbus.emit)
		self.manager.load_modules()

		self.define_core_commands()


	def define_core_commands(self):
		# module manager cannot inspect the core itself
		# so we have to resort to manual registration
		
		self.define_command(
			"shutdown",
			self.shutdown_command,
			"Request Sapphire to shutdown."
		)

		self.define_command(
			"get",
			self.get_command,
			"Get internal values from Sapphire. See 'get help'"
		)

		
	def run(self):
		
		self.manager.start_modules(self.config.dev)

		while self.is_running: 

			if self.eventbus.is_empty():
				if self.shutdown_requested:
					self.shutdown()
					break
				time.sleep(0.05)
				continue
			
			event = self.eventbus.receive() 
			
			self.pass_events(event)


	def pass_events(self, event: SapphireEvents.Event):

		#if self.is_dev:
		#	self.log_events(event)
		event_type = type(event)

		if event_type in self.core_events: 
			self.handle(event)

		if event_type not in self.manager.defined_events():
			return

		for module in self.manager.get_module_list(event_type):
			try:
				module.handle(event) 
			except Exception as e:
				self.catch_error(module, event, e)

				
	def catch_error(self, mod: SapphireModule, event: SapphireEvents.Event, e: Exception):

		self.log(
			SapphireEvents.chain(),
			"critical",
			f"Module '{mod.name()}' could not handle an event! " \
			f"Event = {event}. Encountered Error = {e.__class__.__name__}:{e}"
		)

		if self.config.dev: 
			self.shutdown()
			raise e


	def handle(self, event: SapphireEvents.Event):
		match event:
			case SapphireEvents.ShutdownEvent():
				if event.emergency:
					self.shutdown() 
					return
				self.shutdown_requested = True


	def log(self, chain: SapphireEvents.Chain, level: Literal["debug", "info", "warning", "critical"], msg: str):
		event = SapphireEvents.LogEvent(
			"core",
			SapphireEvents.make_timestamp(),
			chain,
			level,
			msg
		)
		self.eventbus.emit(event)


	def log_events(self, event: SapphireEvents.Event):
		"Logs event to a event.log file. Only works when dev mode is on."

		with open(self.event_logs, "a+") as file:
			file.write(f"{event.__str__()}\n")


	def shutdown(self, ev: SapphireEvents.ShutdownEvent):
		
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
			f"Sapphire is now shutting down. Reason : {ev.reason}"
		)

		logger.handle(event)
		logger.end()


	def define_command(
		self, 
		cmd: str, 
		func: Callable[[list[str], SapphireEvents.Chain], str], 
		info: str = ""
		):
		self.eventbus.emit(
			SapphireEvents.CommandRegisterEvent(
				"core",
				SapphireEvents.make_timestamp(),
				SapphireEvents.chain(),
				"core",
				cmd,
				info,
				func
			)
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
			"User request."
		)
		self.eventbus.emit(event)

		return "Requested Sapphire to shutdown."


	_get_terms = {}
	def get_command(self, args: list[str], chain: SapphireEvents.Chain) -> str:

		if not self._get_terms:
			self._get_terms = {
				"chain" : lambda: SapphireEvents._intern_chain.__str__(),
				"user" : lambda: self.config.get("user.name", "Unknown"),
				"config" : lambda: f"Using config dir : {self.config.directory}",
				"help" : lambda: f"Accessible terms: {[x for x in self._get_terms.keys()]}"
			}

		num_args = len(args)
		if num_args != 1:
			value = self._get_terms["help"]()
			return value
		
		item = args[0]
		value = self._get_terms.get(item, "help")()
		return value


