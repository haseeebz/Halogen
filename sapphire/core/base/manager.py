from .module import SapphireModule
from .config import SapphireConfig
from .events import SapphireEvents
from typing import Callable, MutableSequence, Type
from pathlib import Path

class SapphireModuleManager():

	def __init__(self, root: Path, config: SapphireConfig, emit_event: Callable):
		self.sapphire_root = root
		self.config = config
		self.emit_event = emit_event

		self.modules: MutableSequence[SapphireModule] = []
		self.dispatch_map: dict[type[SapphireEvents.Event], MutableSequence[SapphireModule]] = {}


	def register_module(self, module_class: type[SapphireModule]) -> None:

		module = module_class(
			self.emit_event,
			self.config.get_sub_config(module_class.name())
			)
		self.modules.append(module)

		handled_events = module.handled_events()
		for event in handled_events:
			self.dispatch_map.setdefault(event, []).append(module)


	def start_modules(self):
		for module in self.modules:
			try:
				module.start()
			except Exception as e:
				raise Exception(
					f"Could not start module with name {module.name()} (type:{type(module)})"
				) from e


	def end_modules(self):
		for module in self.modules:
			try:
				success, err = module.end()
			except Exception as e:
				success = False
				err = f"{type(e).__name__} : {str(e)}"

			if success:
				continue

			msg = f"Could not properly end module {module.name()}. {err}" 

			log_event = SapphireEvents.LogEvent(
				sender = "SapphireCore",
				timestamp = SapphireEvents.make_timestamp(),
				chain_id = SapphireEvents.chain(),
				level = "warning",
				message = msg
			) 

			self.emit_event(log_event)

	
	def defined_events(self):
		return self.dispatch_map.keys()
	
	
	def get_module_list(self, event: Type[SapphireEvents.Event]):
		return self.dispatch_map[event]