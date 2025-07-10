from collections.abc import Callable
from typing import Tuple
from sapphire.core.base import (
	SapphireEvents,
	SapphireConfig,
	SapphireModule
)

from .base import BaseModelProvider
from .models import Gemini

core_models = [
	Gemini
]

class ModelManager(SapphireModule):

	def __init__(
		self, 
		emit_event: Callable[[SapphireEvents.Event], None], 
		config: SapphireConfig
	) -> None:
		super().__init__(emit_event, config)
		self.current_model: BaseModelProvider = None #type:ignore / will be assigned
		self.registered_providers: dict[str, BaseModelProvider] = {}

	@classmethod
	def name(cls) -> str:
		return "model"
	
	def start(self) -> None:

		for core_model in core_models:
			model = core_model(self.config.get_sub_config(core_model.name()))
			self.registered_providers[model.name()] = model

		current_model = self.config.get("name", None)
		self.load_model(current_model)


	def handle(self, event: SapphireEvents.Event) -> None:

		match event:
			case SapphireEvents.PromptEvent():
				response_event = self.current_model.generate(event)
				if response_event:
					self.emit_event(response_event)


	def handled_events(self) -> list[type[SapphireEvents.Event]]:
		return [
			SapphireEvents.PromptEvent
		]


	def end(self) -> Tuple[bool, str]:
		if self.current_model:
			self.current_model.unload()
		return (True, "Success")
	

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