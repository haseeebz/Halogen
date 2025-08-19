from collections.abc import Callable
import importlib.util
from pathlib import Path
import os, sys
from types import ModuleType
from typing import Tuple, Union
import inspect, importlib

from halogen.base import (
	HalogenEvents,
	HalogenConfig,
	HalogenModule,
	HalogenError,
	HalogenCommand,
	Chain
)

from .base import (
	BaseModelProvider,
	ModelResponse, 
	HalogenModelResponseError,
	HalogenProviderError
)


class HalogenModelManager(HalogenModule):

	def __init__(
		self, 
		emit_event: Callable[[HalogenEvents.Event], None], 
		config: HalogenConfig
		):
		super().__init__(emit_event, config)
		self.current_provider: Union[BaseModelProvider, None] = None 
		self.registered_providers: dict[str, BaseModelProvider] = {}
		self.model_directory = self.config.directory / "models"
		self.has_commands = True


	@classmethod
	def name(cls) -> str:
		return "model"
	

	def handled_events(self) -> list[type[HalogenEvents.Event]]:
		return [
			HalogenEvents.PromptEvent
		]


	def handle(self, event: HalogenEvents.Event) -> None:

		match event:
			case HalogenEvents.PromptEvent():
				self.generate_response(event)


	def start(self) -> None:
		self.init_providers()
		current_provider = self.config.get("name", None)

		try:
			msg = self.change_provider(current_provider)
			success = True
		except HalogenProviderError as e:
			msg = str(e)
			success = False

		if success:
			self.log(
				HalogenEvents.chain(),
				"info",
				msg
			)
			return

		ev = HalogenEvents.ShutdownEvent(
			self.name(),
			HalogenEvents.make_timestamp(),
			HalogenEvents.chain(),
			True,
			f"{msg}"
		)
		self.emit_event(ev)


	def end(self) -> Tuple[bool, str]:
		if self.current_provider:
			self.current_provider.unload()
		return (True, "Success")


	def init_providers(self):
		"""
		Search and Initialize all model providers.
		All python modules within the model directories are searched for a get_model() 
		method.
		"""

		model_mods = self.import_providers()

		for mod in model_mods:

			model_class = self.get_provider_from_module(mod)

			if not model_class: continue
			model: BaseModelProvider = model_class(
				self.config.get_sub_config(model_class.name())
				)
			
			
			self.registered_providers[model.name()] = model

			self.log(
				HalogenEvents.chain(),
				"info",
				f"Registered Model '{model.name()}'"
			)


	def import_providers(self) -> list[ModuleType]:
		"""
		Get all python modules within models/
		"""
	
		mods = []

		for sub_dir in self.model_directory.iterdir():

			if not sub_dir.is_dir():
				self.log(
					HalogenEvents.chain(),
					"debug",
					f"Ignoring {sub.absolute()}. Not a directory"
				)
				continue
			
			sub_dir_init = sub_dir / "__init__.py"

			if not sub_dir_init.exists():
				self.log(
					HalogenEvents.chain(),
					"debug",
					f"Ignoring {sub_dir.absolute()}. Not a python module."
				)
				continue

			mod_name = sub_dir.name

			spec = importlib.util.spec_from_file_location(mod_name, sub_dir_init)

			if not spec: continue
			if not spec.loader: continue

			mod = importlib.util.module_from_spec(spec)
			sys.modules[mod_name] = mod
			
			spec.loader.exec_module(mod)
			mods.append(mod)
			
		
		return mods
	

	def get_provider_from_module(self, mod: ModuleType) -> type[BaseModelProvider] | None:

		if not hasattr(mod, "get_model"):
			self.log(
				HalogenEvents.chain(),
				"warning",
				f"A python module found in model/: '{mod.__name__}' has no get_model method"
			)
			return None

		model_cls = mod.get_model()

		if not issubclass(model_cls, BaseModelProvider):
			self.log(
				HalogenEvents.chain(),
				"critical",
				f"A python module found in model/: '{mod.__name__}' returned an invalid model provider. " \
				f"Expected BaseModelProvider, Got {type(model_cls)}"
			)
			return None
		
		name = model_cls.name()

		if name in self.registered_providers.keys():

			err = f"A python module found in model/: '{mod.__name__}' " \
			"returned an invalid model provider." \
			f"Model tried to register with name '{name}' but it already exists." \
			"Could lead to security risks in case of API key transfers. Raising Error."

			self.log(
				HalogenEvents.chain(),
				"critical",
				err
			)

			raise HalogenError(err)
		
		return model_cls


	def change_provider(self, provider: str) -> str:
		
		if provider not in self.registered_providers:
			raise HalogenProviderError("Could not find provider '{provider}'. It was not registered.")

		if self.current_provider: self.current_provider.unload()
		self.current_provider = self.registered_providers[provider]
		self.current_provider.load()

		return f"Loaded provider '{provider}'."


	def change_model(self, model: str) -> str:
		return self.current_provider.load(model)


	def generate_response(self, event: HalogenEvents.PromptEvent):

		if not self.current_provider:
			return 
		
		try:
			response = self.current_provider.generate(event)
		except HalogenModelResponseError as e:
			self.log(
			HalogenEvents.chain(event),
			"critical",
			f"Could not get response from model '{self.current_provider.name()}'. " \
			f"Encountered Error: {e.__class__.__name__} : {str(e)}."
			)
			return 

		self.eval_ai_response(response, HalogenEvents.chain(event))

	
	
	def eval_ai_response(self, response: ModelResponse, chain: Chain):

		extras = {}
		for ex in response.extras:
			extras[ex.key] = ex.value
		

		ai_msg = HalogenEvents.AIResponseEvent(
			self.name(),
			HalogenEvents.make_timestamp(),
			chain,
			response.message,
			extras
		)
		self.emit_event(ai_msg)

		for task in response.tasks:
			task_ev = HalogenEvents.TaskEvent(
				self.name(),
				HalogenEvents.make_timestamp(),
				chain,
				task.namespace,
				task.task_name,
				task.args
			)
			self.emit_event(task_ev)


	@HalogenCommand("current", "Get info about the current model")
	def get_current_model_command(self, args: list[str], chain: Chain) -> tuple[bool, str]:
		return (True, f"Model: {self.current_provider.name()}")


	@HalogenCommand("switch", "Switch the model or provider. ARGS: [model/provider] name")
	def switch_command(self, args: list[str], chain: Chain):

		if len(args) != 2:
			raise ValueError(f"Expected 2 args. Got {len(args)}.")

		choice = args[0]
		name = args[1]

		success = True
		match choice:
			case "provider":
				msg = self.change_provider(name)
			case "model":
				msg = self.change_model(name)
			case _:
				success = False
				msg = f"Unknown switch argument : {choice}"

		return (success, msg)
		




