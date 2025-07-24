from collections.abc import Callable
import importlib.util
from pathlib import Path
import os
from types import ModuleType
from typing import Tuple
import inspect, importlib
from sapphire.core.base import (
	SapphireEvents,
	SapphireConfig,
	SapphireModule
)

from .base import BaseModelProvider




class ModelManager(SapphireModule):

	def __init__(
		self, 
		emit_event: Callable[[SapphireEvents.Event], None], 
		config: SapphireConfig
		):
		super().__init__(emit_event, config)
		self.current_model: BaseModelProvider = None #type:ignore / will be assigned
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


	def end(self) -> Tuple[bool, str]:
		if self.current_model:
			self.current_model.unload()
		return (True, "Success")
	

	def start(self) -> None:
		self.init_models()
		current_model = self.config.get("name", None)
		self.load_model(current_model)


	def init_models(self):

		model_mods = self.import_models()
		
		for mod in model_mods:

			if not hasattr(mod, "get_model"):
				continue
			
			model_class = mod.get_model()
			model: BaseModelProvider = model_class(self.config.get_sub_config(model_class.name()))
			self.registered_providers[model.name()] = model

			self.log(
				SapphireEvents.chain(),
				"info",
				f"Registered Model '{model.name()}'"
			)


	def import_models(self) -> list[ModuleType]:
	
		mods = []
		for sub in self.model_directory.iterdir():
			if not sub.is_dir():
				continue
			 
			mod_init = sub / "__init__.py"
			
			if not mod_init.exists():
				pass #Error here

			mod_name = f"models.{sub.name}"
			spec = importlib.util.spec_from_file_location(mod_name, mod_init)

			if not spec: continue
			if not spec.loader: continue

			mod = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(mod)

			mods.append(mod)
		
		return mods
			


	def generate_response(self, event: SapphireEvents.PromptEvent):
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
	

	def load_model(self, model: str) -> None:

		if self.current_model: 
			self.current_model.unload()

		if model not in self.registered_providers.keys():

			event = SapphireEvents.ShutdownEvent(
				self.name(),
				SapphireEvents.make_timestamp(),
				SapphireEvents.chain(),
				True,
				"critical"
			)

			self.emit_event(event)

			self.log(
				SapphireEvents.chain(event),
				"critical",
				f"Could not find model '{model}'. It was not registered."
			)

		self.current_model = self.registered_providers[model]
		self.current_model.load()

		self.log(
			SapphireEvents.chain(),
			"info",
			f"Loaded model '{model}'."
		)	