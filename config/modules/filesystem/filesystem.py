from collections.abc import Callable
from typing import Tuple
from pathlib import Path
import os, shutil, re
from halogen.base import HalogenEvents, HalogenModule, HalogenConfig
from halogen.modules.tasks.base import HalogenTask



class FileSystem(HalogenModule):
	
	def __init__(self, emit_event: Callable[[HalogenEvents.Event], None], config: HalogenConfig) -> None:
		super().__init__(emit_event, config)
		self.has_tasks = True


	@classmethod
	def name(cls):
		return "filesystem"
	

	def handled_events(self) -> list[type[HalogenEvents.Event]]:
		return []
	

	def start(self) -> None:
		pass


	def end(self) -> Tuple[bool, str]:
		return (True, "No specific end action needed.")
	

	@HalogenTask("read_file", "Read the contents of a file.", ["path:str", "lines:int"])
	def read_file(self, chain: HalogenEvents.chain, path_raw: str, lines: str):

		path = Path(path_raw)
		lines = int(lines) if lines.isdigit() else 10

		with open(path) as file:
			content = [file.readline() for _ in range(lines)]

		return "".join(content)

	
	@HalogenTask("write_to_file", "Write content to a file.", ["path:str", "content:str"])
	def write_file(self, chain: HalogenEvents.chain, path_raw: str, content: str):

		path = Path(path_raw)

		with open(path, "w") as file:
			content = file.write(content)

		return f"Successfully written to {path_raw}"

	
	@HalogenTask("append_to_file", "Append content to a file.", ["path:str", "content:str"])
	def append_file(self, chain: HalogenEvents.chain, path_raw: str, content: str):

		path = Path(path_raw)

		with open(path, "a") as file:
			content = file.write(content)

		return f"Successfully appended to {path_raw}"


	@HalogenTask("list_directory", "List the contents of a directory/folder.", ["path:str"])
	def list_directory(self, chain: HalogenEvents.Chain, path_raw: str):

		path = Path(path_raw)

		if not path.is_dir():
			return f"{path} is not a directory!"

		contents = [item.name for item in path.iterdir()]

		if len(contents) > 16:
			return f"{contents[0:17]} + {len(contents)-16} items truncated to not overwhelm the AI."
		else:
			return contents


	@HalogenTask("make_directory", "Creates a directory along with missing parents", ["path:str"])
	def make_directory(self, chain: HalogenEvents.Chain, path: str):

		path = Path(path)

		if path.exists():
			return f"{path} already exists!"

		path.mkdir(0o777, True, True)

		return f"Created directory at {path}."


	@HalogenTask("remove_directory", "Deletes a directory recursively! Dangerous", ["path:str"])
	def remove_directory(self, chain: HalogenEvents.Chain, path: str):

		path = Path(path)

		if not path.exists():
			return f"{path} does not exists!"

		if not path.is_dir():
			return f"{path} is not a directory or folder."
			
		shutil.rmtree(path)

		return f"Removed directory at {path}."


	@HalogenTask("create_file", "Create a file at the specified location, extension included.", ["path:str"])
	def create_file(self, chain: HalogenEvents.Chain, path: str):

		path = Path(path)

		if path.exists():
			return f"Path {path} already exists. Did not create a file."

		open(path, "x").close()

		return f"Created file at {path}."


	@HalogenTask("remove_file", "Remove a file at the specified location.", ["path:str"])
	def remove_file(self, chain: HalogenEvents.Chain, path: str):

		path = Path(path)

		if not path.exists():
			return f"Path {path} does not exist. Did not remove the file."

		os.remove(path)

		return f"Removed file at {path}."


	@HalogenTask("search_file", "Search for a file within a given directory.", ["name:str","directory:str"])
	def search_file(self, chain: HalogenEvents.Chain, name: str, directory: str):

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

		if len(found) > 16:
			return f"{found[0:17]} + {len(found)-16} files truncated to not overwhelm the AI."
		else:
			return found


	@HalogenTask(
		"regex_file_search",
		"Search files within a directory by a given a regex pattern. The pattern arg must be valid regex.",
		["directory:str", "pattern:str"]
	)
	def regex_search_file(self, chain: HalogenEvents.Chain, directory: str, pattern: str):

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

		if len(found) > 16:
			return f"{found[0:17]} + {len(found)-16} files truncated to not overwhelm the AI."
		else:
			return found





