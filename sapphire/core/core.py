import time
from typing import MutableSequence
from .base import EventBus, Event, SapphireModule, SapphireConfig, SapphireEvents


class SapphireCore():

	def __init__(self) -> None:
		self.eventbus: EventBus = EventBus()
		self.is_running: bool = True

		self.modules: MutableSequence[SapphireModule] = []
		self.dispatch_map: dict[type[Event], MutableSequence[SapphireModule]] = {}

		self.config: SapphireConfig = SapphireConfig()

		self.core_events: MutableSequence[type[Event]] = [
			SapphireEvents.ShutdownEvent
		]


	def register_module(self, module_class: type[SapphireModule]) -> None:
		module = module_class(self.eventbus.emit)
		self.modules.append(module)
		handled_events = module.handled_events()
		for event in handled_events:
			self.dispatch_map.setdefault(event, []).append(module)

	def run(self):
		while self.is_running:

			if self.eventbus.is_empty():
				time.sleep(0.05)
				continue
			
			event = self.eventbus.receive()
			event_type = type(event)

			if event_type in self.dispatch_map.keys():
				for module in self.dispatch_map[event_type]:
					module.handle(event)

	def start_modules(self):
		for module in self.modules:
			try:
				module.start()
			except Exception as e:
				raise Exception(
					f"Could not start module with name {module.name()} (type:{type(module)})"
				)

	def shutdown(self):
		pass
