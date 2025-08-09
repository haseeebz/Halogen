import tomllib, os
from typing import Any, Union
import platform
from pathlib import Path
from dataclasses import dataclass

from .error import SapphireError


class SapphireConfig():
	"""
	Dataclass containing basic info and the contents of the config file.
	Only the segment with the same name as the module will be passed from the config file.

	For example,

	The PromptManager module has name 'prompt' and thus only the [prompt] section is passed to it 
	in the cfg field. The prompt manager can then just access 'memory_limit' or anyother field inside 
	[prompt] without having to acces prompt.memory_limit.

	Similarly, a specifc model will get only its config. For example, the gemini model will get the 
	[model.gemini] field.
	"""

	def __init__(self, os: str, directory: str, cfg: dict[str, Any]):
		self._os = os
		self._directory = directory
		self._cfg = cfg

	@property
	def os(self):
		return self._os

	@property
	def directory(self):
		return self._directory

	def get(self, path: str, default: Any = None) -> Any:	
		parts = path.split(".")
		current = self.cfg
		for part in parts:
			if isinstance(current, dict):
				current = current.get(part, default)

		return current


	def get_sub_config():
		cfg = self.get(path, {})
		
		if not isinstance(cfg, dict):
			cfg = {}

		return SapphireConfig(self._os, self._directory, cfg=cfg)



class SapphireConfigLoader():

	def __init__(self):

		self.os = platform.system().lower()
		self.init_config()

		self.file: str           = ""
		self.directory: str		 = ""
		self.cfg: dict[str, Any] = {}	


	def init_config(self):

		if self.os == "windows":
			self.directory = Path(os.environ["APPDATA"]) / "sapphire"
		elif self.os == "linux":
			self.directory = Path(os.path.expanduser("~/.config/sapphire"))
		else:
			raise SapphireError(f"Running in unsupported operating system: {OS}.")

		if not self.directory.exists():
			os.makedirs(CONFIG_DIR, exist_ok = True)


	def load(self):
		
		self.file = self.directory / "config.toml"

		if not self.file.exists():
			raise SapphireError(f"Config file '{self.file}' does not exist! Cannot start sapphire.")

		with open(self.file) as file:
			try:
				data = tomllib.load(file)
			except tomllib.TOMLDecodeError:
				raise SapphireError(f"Invalid config file '{self.file}'.")

		self.cfg = SapphireConfig(
			self.os,
			self.directory,
			self.cfg
		)

		return self.cfg

	
	