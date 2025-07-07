from collections.abc import Callable
from sapphire.core.base import (
	SapphireEvents,
	SapphireConfig,
	SapphireModule
)

from .base import BaseModel


class ModelManager(SapphireModule):

	def __init__(
		self, 
		emit_event: Callable[[SapphireEvents.Event], None], 
		config: SapphireConfig
	) -> None:
		super().__init__(emit_event, config)
		self.current_model: BaseModel | None = None

	@classmethod
	def name(cls) -> str:
		return "model"
	
	def start(self) -> None:
		self.config.get("name", None)