from collections.abc import Callable
from typing import Tuple
from sapphire.base import SapphireEvents, SapphireModule, SapphireConfig, SapphireTask



class FileSystem(SapphireModule):
	
	def __init__(self, emit_event: Callable[[SapphireEvents.Event], None], config: SapphireConfig) -> None:
		super().__init__(emit_event, config)
		self.has_tasks = True

	@classmethod
	def name(cls):
		return "filesystem"
	
	def handled_events(self) -> list[type[SapphireEvents.Event]]:
		return []
	
	def start(self) -> None:
		pass

	def end(self) -> Tuple[bool, str]:
		return (False, "testing!")
	
	@SapphireTask("read_file", "Read the contents of a file.", ["path:str"])
	def read_file(self, args: list[str], chain: SapphireEvents.Chain):
		with open(args[0]) as file:
			return file.read()