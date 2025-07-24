from dataclasses import dataclass, field
from typing import Callable
from sapphire.core.base import SapphireEvents

@dataclass
class CommandData:
	cmd: str
	info: str
	func: Callable[[list[str], SapphireEvents.Chain], str]

@dataclass 
class CommandNamespace:
	module: str
	defined: set[str] = field(default_factory = set)
	commands: dict[str, CommandData] = field(default_factory = dict)