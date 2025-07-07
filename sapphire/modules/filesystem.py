from collections.abc import Callable
from typing import Tuple
from sapphire.core.base import SapphireEvents, SapphireModule
from sapphire.core.base.config import SapphireConfig

def get_module():
	return FileSystem

class FileSystem(SapphireModule):
	
	def __init__(self, emit_event: Callable[[SapphireEvents.Event], None], config: SapphireConfig) -> None:
		super().__init__(emit_event, config)

	@classmethod
	def name(cls):
		return "filesystem"
	
	def handled_events(self) -> list[type[SapphireEvents.Event]]:
		return []
	
	def start(self) -> None:
		pass

	def end(self) -> Tuple[bool, str]:
		return (False, "testing!")
	