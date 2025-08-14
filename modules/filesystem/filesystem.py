from collections.abc import Callable
from typing import Tuple
from pathlib import Path
import os, shutil, re
from sapphire.base import SapphireEvents, SapphireModule, SapphireConfig, SapphireTask



class FileSystem(SapphireModule):
	
	def __init__(self, emit_event: Callable[[SapphireEvents.Event], None], config: SapphireConfig) -> None:
		super().__init__(emit_event, config)
		self.has_tasks = True


	@property
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

	
	@SapphireTask("write_to_file", "Write content to a file.", ["path:str", "content:str"])
	def write_file(self, chain: SapphireEvents.chain, path_raw: str, content: str):

		path = Path(path_raw)

		with open(path, "w") as file:
			content = file.write(content)

		return f"Successfully written to {path_raw}"

	
	@SapphireTask("append_to_file", "Append content to a file.", ["path:str", "content:str"])
	def append_file(self, chain: SapphireEvents.chain, path_raw: str, content: str):

		path = Path(path_raw)

		with open(path, "a") as file:
			content = file.write(content)

		return f"Successfully appended to {path_raw}"


	@SapphireTask("list_directory", "List the contents of a directory/folder.", ["path:str"])
	def list_directory(self, chain: SapphireEvents.Chain, path_raw: str):

		path = Path(path_raw)

		if not path.is_dir():
			return f"{path} is not a directory!"

		contents = [item.name for item in path.iterdir()]

		return contents


	@SapphireTask("make_directory", "Creates a directory along with missing parents", ["path:str"])
	def make_directory(self, chain: SapphireEvents.Chain, path: str):

		path = Path(path)

		if path.exists():
			return f"{path} already exists!"

		path.mkdir(0o777, True, True)


	@SapphireTask("remove_directory", "Deletes a directory recursively! Dangerous", ["path:str"])
	def remove_directory(self, chain: SapphireEvents.Chain, path: str):

		path = Path(path)

		if not path.exists():
			return f"{path} does not exists!"

		if not path.is_dir():
			return f"{path} is not a directory or folder."
			
		shutil.rmtree(path)


	@SapphireTask("create_file", "Create a file at the specified location, extension included.", ["path:str"])
	def create_file(self, chain: SapphireEvents.Chain, path: str):

		path = Path(path)

		if path.exists():
			return f"Path {path} already exists. Did not create a file."

		open(path, "x").close()

	

	@SapphireTask("remove_file", "Remove a file at the specified location.", ["path:str"])
	def remove_file(self, chain: SapphireEvents.Chain, path: str):

		path = Path(path)

		if not path.exists():
			return f"Path {path} does not exist. Did not remove the file."

		os.remove(path)



	@SapphireTask("search_file", "Search for a file within a given directory.", ["name:str","directory:str"])
	def search_file(self, chain: SapphireEvents.Chain, name: str, directory: str):

		path = Path(directory)

		if not path.is_dir():
			return f"{path} is not a directory!"

		found = []
		for item in path.iterdir():
			if item.is_dir():
				sub_found = self.search_file(chain, name, item.absolute())
				found.extend(sub_found)
				continue

			if item.name == name:
				found.append(item.__str__())

		return found


	@SapphireTask(
		"regex_file_search",
		"Search files within a directory by a given a regex pattern. The pattern arg must be valid regex.",
		["directory:str", "pattern:str"]
	)
	def regex_search_file(self, chain: SapphireEvents.Chain, directory: str, pattern: str):

		path = Path(directory)

		if not path.exists():
			return f"{path} does not exist. Cannot conduct regex search."

		try: 
			regex_compiled = re.compile(pattern)
		except re.error:
			return f"Invalid regex pattern: {pattern}"

		found = []

		for item in path.iterdir():
			if item.is_dir():
				sub_found = self.regex_search_file(chain, item.absolute(), pattern)
				found.extend(sub_found)
				continue

			if regex_compiled.search(item.name):
				found.append(item.__str__())

		return found





