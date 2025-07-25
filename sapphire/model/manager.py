from collections.abc import Callable
import importlib.util
from pathlib import Path
import os
from types import ModuleType
from typing import Tuple, Union
import inspect, importlib

from sapphire.core.base import (
	SapphireEvents,
	SapphireConfig,
	SapphireModule,
	SapphireError
)

from .base import BaseModelProvider




class ModelManager(SapphireModule):

	def __init__(
		self, 
		emit_event: Callable[[SapphireEvents.Event], None], 
		config: SapphireConfig
		):
		super().__init__(emit_event, config)
		self.current_model: Union[BaseModelProvider, None] = None 
		self.registered_providers: dict[str, BaseModelProvider] = {}
		self.model_directory = Path("models/")


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
		self.init_models()
		current_model = self.config.get("name", None)
		self.load_model(current_model)


	def end(self) -> Tuple[bool, str]:
		if self.current_model:
			self.current_model.unload()
		return (True, "Success")


	def init_models(self):
		"""
		Search and Initialize all model providers.
		All python modules within the model directories are searched for a get_model() 
		method.
		"""

		model_mods = self.import_models()
		
		for mod in model_mods:

			model_class = self.get_model_from_module(mod)

			if not model_class: continue

			model: BaseModelProvider = model_class(self.config.get_sub_config(model_class.name()))
			self.registered_providers[model.name()] = model

			self.log(
				SapphireEvents.chain(),
				"info",
				f"Registered Model '{model.name()}'"
			)


	def import_models(self) -> list[ModuleType]:
		"""
		Get all model classes returned by get_model() of all python modules within models/
		"""
	
		mods = []

		for sub in self.model_directory.iterdir():

			if not sub.is_dir():
				continue
			 
			mod_init = sub / "__init__.py"
			
			if not mod_init.exists():
				self.log(
					SapphireEvents.chain(),
					"debug",
					f"Ignoring {sub.absolute()}. Not a python module."
				)
				continue

			mod_name = f"models.{sub.name}"

			spec = importlib.util.spec_from_file_location(mod_name, mod_init)

			if not spec: continue
			if not spec.loader: continue

			mod = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(mod)
			mods.append(mod)
		
		return mods
	

	def get_model_from_module(self, mod: ModuleType) -> type[BaseModelProvider] | None:

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


			

	def load_model(self, model: str) -> None:

		if self.current_model: 
			self.current_model.unload()

		if model not in self.registered_providers.keys():

			self.log(
				SapphireEvents.chain(),
				"critical",
				f"Could not find model '{model}'. It was not registered."
			)

			if self.current_model:
				return
			
			event = SapphireEvents.ShutdownEvent(
				self.name(),
				SapphireEvents.make_timestamp(),
				SapphireEvents.chain(),
				True,
				"critical",
				f"Could not find model '{model}'. It was not registered."
			)

			self.emit_event(event)

			return
		

		self.current_model = self.registered_providers[model]
		self.current_model.load()

		self.log(
			SapphireEvents.chain(),
			"info",
			f"Loaded model '{model}'."
		)	

	
	def generate_response(self, event: SapphireEvents.PromptEvent):

		if not self.current_model:
			return # TODO error?
		
		response = self.current_model.generate(event)

		if response is not None:
			
			extras = {}
			for ex in response.extras:
				extras[ex.key] = ex.value
			
			ai_msg = SapphireEvents.AIResponseEvent(
				self.name(),
				SapphireEvents.make_timestamp(),
				SapphireEvents.chain(event),
				response.message,
				extras
			)

			self.emit_event(ai_msg)

			return

		self.log(
				SapphireEvents.chain(event),
				"critical",
				f"Could not get response from model '{self.current_model.name()}'"
			)
	

