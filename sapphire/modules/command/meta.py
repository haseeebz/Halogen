from dataclasses import dataclass, field
from typing import Callable
from sapphire.base import Chain

@dataclass
class CommandData:
	cmd: str
	info: str
	func: Callable[[list[str], Chain], str]

@dataclass 
class CommandNamespace:
	module: str
	defined: set[str] = field(default_factory = set)
	commands: dict[str, CommandData] = field(default_factory = dict)