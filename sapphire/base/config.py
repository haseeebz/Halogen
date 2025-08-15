import tomllib, os, argparse
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

	def __init__(self, os: str, directory: Path, cfg: dict[str, Any], dev: bool):
		self._os = os
		self._directory = directory
		self._cfg = cfg
		self._dev = dev

	@property
	def os(self):
		return self._os

	@property
	def directory(self):
		return self._directory

	@property
	def dev(self):
		return self._dev

	def get(self, path: str, default: Any = None) -> Any:	
		parts = path.split(".")
		current = self._cfg
		for part in parts:
			if isinstance(current, dict):
				current = current.get(part, default)

		return current


	def get_sub_config(self, path: str):
		cfg = self.get(path, {})
		
		if not isinstance(cfg, dict):
			cfg = {}

		return SapphireConfig(self._os, self._directory, cfg, self._dev)



class SapphireConfigLoader():

	def __init__(self):

		self.os = platform.system().lower()
		self.make_parser()
		

		self.config_file: Path         
		self.directory: Path	 
		self.cfg: dict[str, Any] = {}	
		
		args = self.load_args()
		self.dev = args.dev
		self.configdir = args.configdir

		if self.configdir:
			self.init_config(Path(self.configdir))
		else:
			self.init_default_config()
	
	
	def make_parser(self):

		self.parser = argparse.ArgumentParser(
			prog = "sapphire",
			description = "Boots up Sapphire. See --help for help."
		)

		self.parser.add_argument(
			"--dev", 
			help = "Run sapphire in dev mode.", 
			default = False, 
			action = "store_true"
		)

		self.parser.add_argument(
			"--configdir", 
			help = "Run sapphire in dev mode.", 
			type = str
		)


	def load_args(self):
		args = self.parser.parse_args()
		return args


	def init_config(self, directory: Path):
		if not directory.exists():
			print(f"Invalid Config Directory : {directory}")
			
		self.directory = directory


	def init_default_config(self):

		if self.os == "windows":
			self.directory = Path(os.environ["APPDATA"]) / "sapphire"
		elif self.os == "linux":
			self.directory = Path(os.path.expanduser("~/.config/sapphire"))
		else:
			raise SapphireError(f"Running in unsupported operating system: {OS}.")

		if not self.directory.exists():
			os.makedirs(self.directory, exist_ok = True)


	def load(self):
		
		self.config_file = self.directory / "config.toml"

		if not self.config_file.exists():
			raise SapphireError(f"Config file '{self.config_file}' does not exist! Cannot start sapphire.")

		with open(self.config_file, 'rb') as file:
			try:
				data = tomllib.load(file)
			except tomllib.TOMLDecodeError:
				raise SapphireError(f"Invalid config file '{self.config_file}'.")

		cfg = SapphireConfig(
			self.os,
			self.directory,
			data,
			self.dev
		)

		return cfg

	
	