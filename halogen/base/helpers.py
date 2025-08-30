import importlib, sys
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

	def from_file(self, name: str, file_path: Path | str) -> ModuleType:
		"Loading module from a file. Raises PyModuleError on any failure."
		
		if type(file_path) is str: file_path = Path(file_path)

		if not file_path.exists():
			raise PyModuleLoader.PyModuleError(f"{file_path.absolute()} does not exist.")
		
		if not file_path.is_file():
			raise PyModuleLoader.PyModuleError(f"{file_path.absolute()} is not a file!")


		spec = util.spec_from_file_location(name, file_path)

		if not spec or not spec.loader:
			raise PyModuleLoader.PyModuleError(
				f"Could not load spec and spec.loader for module from {file_path.absolute()}."
				)

		mod = util.module_from_spec(spec)
		sys.modules[name] = mod

		try:
			spec.loader.exec_module(mod)
		except Exception as e:
			raise PyModuleLoader.PyModuleError(
				f"Failed to execute module from {file_path.absolute()}."
				) from e

		return mod

	
	def from_directory(self, name: str, dir_path: Path | str) -> ModuleType:
		"Loading a module from a directory. __init__.py must be present."

		if type(dir_path) is str: dir_path = Path(dir_path)

		if not dir_path.is_dir():
			raise PyModuleLoader.PyModuleError(
				f"{dir_path.absolute()} is not a directory."
			)

		file_path = dir_path / "__init__.py"
		mod = self.from_file(name, file_path)
		return mod
