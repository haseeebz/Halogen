import importlib
from importlib import util
from pathlib import Path
from types import ModuleType


class PyModuleLoader():
	"""
	Helper class to load modules from directories/files.
	Made mainly to abstract the shared functionality in Model Manager and  Module Manager.
	"""

	class PyModuleError(Exception):
		def __init__(self, *args: object) -> None:
			super().__init__(*args)


	def __init__(self):
		pass

	def from_file(self, file_path: Path) -> ModuleType:

		if not file_path.exists():
			raise PyModuleLoader.PyModuleError(f"{file_path.absolute()} does not exist.")
		
		if not file_path.is_file():
			raise PyModuleLoader.PyModuleError(f"{file_path.absolute()} is not a file!")

		mod_name = file_path.name.split(".")[0]

		spec = util.spec_from_file_location(mod_name, file_path)

		if not spec or spec.loader:
			raise PyModuleLoader.PyModuleError(
				f"Could not load spec and spec.loader for module at {file_path.absolute()}"
				)
			

		
		
		
