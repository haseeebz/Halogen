import tomllib, os
from typing import Any, Union, TypeVar

T = TypeVar("T")


class SapphireConfig():

	def __init__(self, *, configfile: str = "config.toml", cfg: dict[str, Any] | None = None):

		if isinstance(cfg, dict):
			self.cfg: dict[str, Any] = cfg
		
		self.cfg_file = configfile
		
		try:
			with open(configfile, "rb") as file:
				data = tomllib.load(file)
		except FileNotFoundError as e:
			raise FileNotFoundError(
				f"Config file '{os.path.abspath("config.toml")}' does not Exist"
			) from e
		
		self.cfg = data

	def get(self, path: str, default: T = None) -> Union[T, "SapphireConfig"]:
		parts = path.split(".")
		current = self.cfg
		for part in parts:
			if isinstance(current, dict):
				current = current.get(part, default)
		
		if isinstance(current, dict):
			return SapphireConfig(cfg=current)
		return current
			
