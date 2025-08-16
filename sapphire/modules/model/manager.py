from collections.abc import Callable
import importlib.util
from pathlib import Path
import os, sys
from types import ModuleType
from typing import Tuple, Union
import inspect, importlib

from sapphire.base import (
	SapphireEvents,
	SapphireConfig,
	SapphireModule,
	SapphireError,
	SapphireCommand,
	Chain
)

from .base import BaseModelProvider, ModelResponse

# TODO make module loading better

class SapphireModelManager(SapphireModule):

	def __init__(
		self, 
		emit_event: Callable[[SapphireEvents.Event], None], 
		config: SapphireConfig
		):
		super().__init__(emit_event, config)
		self.current_provider: Union[BaseModelProvider, None] = None 
		self.registered_providers: dict[str, BaseModelProvider] = {}
		self.model_directory = self.config.directory / "models"
		self.has_commands = True


	@classmethod
	def name(cls) -> str:
		return "model"
	

	def handled_events(self) -> list[type[SapphireEvents.Event]]:
		return [
			SapphireEvents.PromptEvent
		]


	def handle(self, event: SapphireEvents.Event) -> None:

		match event:
			case SapphireEvents.PromptEvent():
				self.generate_response(event)


	def start(self) -> None:
		self.init_providers()
		current_provider = self.config.get("name", None)
		success, output = self.load_provider(current_provider)

		if success:
			self.log(
				SapphireEvents.chain(),
				"info",
				output
			)
			return

		ev = SapphireEvents.ShutdownEvent(
			self.name(),
			SapphireEvents.make_timestamp(),
			SapphireEvents.chain(),
			True,
			output
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
				SapphireEvents.chain(),
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
					SapphireEvents.chain(),
					"debug",
					f"Ignoring {sub.absolute()}. Not a directory"
				)
				continue
			
			sub_dir_init = sub_dir / "__init__.py"

			if not sub_dir_init.exists():
				self.log(
					SapphireEvents.chain(),
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
				SapphireEvents.chain(),
				"warning",
				f"A python module found in model/: '{mod.__name__}' has no get_model method"
			)
			return None

		model_cls = mod.get_model()

		if not issubclass(model_cls, BaseModelProvider):
			self.log(
				SapphireEvents.chain(),
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
				SapphireEvents.chain(),
				"critical",
				err
			)

			raise SapphireError(err)
		
		return model_cls

	# The only reason the next two functions return weird values is that i wanted to reuse their logic
	# for both the normal flow and using them in commands.
	# Maybe make this better in the future?

	def load_provider(self, provider: str) -> tuple[bool, str]:
		
		if provider not in self.registered_providers.keys():
			
			msg = f"Could not find provider '{provider}'. It was not registered."
			return (False, msg)

		if self.current_provider: self.current_provider.unload()
		self.current_provider = self.registered_providers[provider]
		self.current_provider.load()

		msg = f"Loaded provider '{provider}'."

		return (True, msg)


	def switch_provider_model(self, model: str, chain: SapphireEvents.Chain) -> tuple[bool, str]:

		success, output = self.current_provider.switch_model(model)

		self.log(
			chain,
			"info" if success else "warning",
			output
		)
		
		return (success, output)
	

	def generate_response(self, event: SapphireEvents.PromptEvent):

		if not self.current_provider:
			return 
		
		response = self.current_provider.generate(event)

		if response is not None:
			self.eval_ai_response(response, SapphireEvents.chain(event))
			return

		self.log(
			SapphireEvents.chain(event),
			"critical",
			f"Could not get response from model '{self.current_provider.name()}'"
			)
	
	
	def eval_ai_response(self, response: ModelResponse, chain: Chain):

		extras = {}
		for ex in response.extras:
			extras[ex.key] = ex.value
		

		ai_msg = SapphireEvents.AIResponseEvent(
			self.name(),
			SapphireEvents.make_timestamp(),
			chain,
			response.message,
			extras
		)
		self.emit_event(ai_msg)

		for task in response.tasks:
			task_ev = SapphireEvents.TaskEvent(
				self.name(),
				SapphireEvents.make_timestamp(),
				chain,
				task.namespace,
				task.task_name,
				task.args
			)
			self.emit_event(task_ev)


	@SapphireCommand("current", "Get info about the current model")
	def get_current_model_command(self, args: list[str], chain: Chain) -> tuple[bool, str]:
		return (True, f"Model: {self.current_provider.name()}")


	@SapphireCommand("switch", "Switch the model or provider. ARGS: [model/provider] name")
	def switch_command(self, args: list[str], chain: Chain):

		if len(args) != 2:
			raise ValueError(f"Expected 2 args. Got {len(args)}.")

		choice = args[0]
		name = args[1]

		match choice:
			case "provider":
				success, msg = self.load_provider(name)
			case "model":
				success, msg = self.switch_provider_model(name)
			case _:
				success = False
				msg = f"Unknown switch argument : {choice}"

		return (success, msg)
		




