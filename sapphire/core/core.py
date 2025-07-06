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
		self.manager = SapphireModuleManager(self.root, self.config, self.eventbus.emit)

		self.command = SapphireCommands(self.eventbus.emit)
		self.define_core_commands()

		self.core_events: MutableSequence[type[SapphireEvents.Event]] = [
			SapphireEvents.ShutdownEvent,
			SapphireEvents.InputEvent
		]

		self.is_running: bool = True
		self.shutdown_requested = False

	
	def run(self):

		self.manager.start_modules()
		
		while self.is_running:

			if self.eventbus.is_empty():
				if self.shutdown_requested:
					self.shutdown()
					break
				time.sleep(0.05)
				continue
			
			event = self.eventbus.receive()
			event_type = type(event)

			if event_type in self.core_events:
				self.handle(event)

			if event_type in self.manager.defined_events():
				for module in self.manager.get_module_list(event_type):
					module.handle(event)


	def handle(self, event: SapphireEvents.Event):
		match event:
			case SapphireEvents.ShutdownEvent():
				if event.emergency:
					self.shutdown() 
					return
				self.shutdown_requested = True
			case SapphireEvents.InputEvent():
				if event.category == "command":
					self.command.interpret(event)


	def log(self, chain_id: int, level: Literal["debug", "info", "warning", "critical"], msg: str):
		event = SapphireEvents.LogEvent(
			"core",
			SapphireEvents.make_timestamp(),
			chain_id,
			level,
			msg
		)
		self.eventbus.emit(event)


	def shutdown(self):
		self.is_running = False
		self.manager.end_modules()


	def define_core_commands(self):
		self.command.define(
			self.shutdown_command,
			"shutdown",
			"Request Sapphire to shutdown. Args: []"
		)

	def shutdown_command(self, args: list[str], chain: int):
		
		self.log(
			chain,
			"info",
			f"Client with chain id {chain} requested sapphire to shutdown. Shutting down."
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