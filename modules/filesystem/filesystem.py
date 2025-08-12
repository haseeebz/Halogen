from collections.abc import Callable
from typing import Tuple
from pathlib import Path
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
		return (True, "")
	

	@SapphireTask("read_file", "Read the contents of a file.", ["path:str", "lines:int"])
	def read_file(self, chain: SapphireEvents.chain, path_raw: str, lines: str):

		path = Path(path_raw)
		lines = int(lines) if lines.isdigit() else 10

		with open(path) as file:
			content = file.readlines(lines)

		return "".join(content)


	@SapphireTask("list_directory", "List the contents of a directory/folder.", ["path:str"])
	def list_directory(self, chain: SapphireEvents.Chain, path_raw: str):

		path = Path(path_raw)

		if not path.is_dir():
			raise ValueError(f"{path} is not a directory!")

		contents = [item.name for item in path.iterdir()]

		return contents