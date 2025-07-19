from types import MethodType
from .module import SapphireModule
from .config import SapphireConfig
from .events import SapphireEvents

from typing import Callable, MutableSequence, Type, Literal
from pathlib import Path
import importlib


# loading the core modules
from sapphire.logger import Logger
from sapphire.interface import SapphireServer
from sapphire.prompt import PromptManager
from sapphire.model import ModelManager
from sapphire.command import CommandHandler

core_modules = [
	Logger, 
	SapphireServer,
	PromptManager,
	ModelManager,
	CommandHandler
]


class SapphireModuleManager():

	def __init__(self, root: Path, config: SapphireConfig, emit_event: Callable):
		self.sapphire_root = root
		self.modules_dir = self.sapphire_root / "modules"

		self.config = config
		self.emit_event = emit_event

		self.modules: MutableSequence[SapphireModule] = []
		self.dispatch_map: dict[type[SapphireEvents.Event], MutableSequence[SapphireModule]] = {}


	def register_module(self, module_class: type[SapphireModule]) -> None:

		valid = isinstance(module_class, type) and issubclass(module_class, SapphireModule)

		if not valid:
			self.log(
				SapphireEvents.chain(),
				"warning",
				f"An argument of type {module_class.__name__} as passed to manager. "\
				"Not a Sapphire Module!"
			)
			return

		module = module_class(
			self.emit_event,
			self.config.get_sub_config(module_class.name())
			)
		self.modules.append(module)

		handled_events = module.handled_events()
		for event in handled_events:
			self.dispatch_map.setdefault(event, []).append(module)

		self.log(
			SapphireEvents.chain(),
			"info",
			f"Loaded module '{module.name()}'. " \
			f"It handles events: {[e.__name__ for e in handled_events]}"
		)


	def load_modules(self) -> None:

		for core_module in core_modules:
			self.register_module(core_module)

		module_names: list[str] = self.config.get("modules", [])

		for module_name in module_names:
			module = self.get_module(module_name)

			if module is None: continue

			self.register_module(module)
			
	
	def get_module(self, name: str) -> type[SapphireModule] | None:

		try:
			py_module = importlib.import_module(f"modules.{name}")
		except ModuleNotFoundError as e:
			self.log(
				SapphireEvents.chain(),
				"warning",
				f"Could not load module '{name}'. " \
				f"The module does not exist or was'nt found. ({e.__class__.name}:{e})"
			)
			return None

		if hasattr(py_module, "get_module"):
			module: type[SapphireModule] = py_module.get_module()
			return module
		else:
			self.log(
				SapphireEvents.chain(),
				"warning",
				f"Could not load module '{name}'. " \
				"The module does not define a standard 'get_module' method which should return a " \
				"Sapphire module."
			)
			return None
		

	def start_modules(self):
		for module in self.modules:
			try:
				module.start()
			except Exception as e:

				self.log(
					SapphireEvents.chain(),
					"critical",
					f"Could not start module with name {module.name()} (type:{type(module)}). " \
					f"Encountered Error = {e.__class__.__name__}:{e}. " \
					"Shutting down sapphire!"
				)

				event = SapphireEvents.ShutdownEvent(
					"module",
					SapphireEvents.make_timestamp(),
					SapphireEvents.chain(),
					True,
					"critical"
				)
				
				self.emit_event(event)


	def end_modules(self) -> Logger | None:
		logger = None
		for module in self.modules:

			if isinstance(module, Logger): 
				logger = module
				continue

			try:
				success, err = module.end()
			except Exception as e:
				success = False
				err = f"{type(e).__name__} : {str(e)}"

			if success:
				continue

			msg = f"Could not properly end module '{module.name()}'. Error: {err}" 

			log_event = SapphireEvents.LogEvent(
				sender = "module",
				timestamp = SapphireEvents.make_timestamp(),
				chain = SapphireEvents.chain(),
				level = "warning",
				message = msg
			) 
			
			self.emit_event(log_event)

		return logger

	
	def defined_events(self):
		return self.dispatch_map.keys()
	

	def get_module_list(self, event: Type[SapphireEvents.Event]):
		return self.dispatch_map[event]
	

	def log(self, chain: SapphireEvents.Chain, level: Literal["debug", "info", "warning", "critical"], msg: str):
		event = SapphireEvents.LogEvent(
			"module",
			SapphireEvents.make_timestamp(),
			chain,
			level,
			msg
		)
		self.emit_event(event)