from dataclasses import dataclass, field
from typing import Callable
from sapphire.core.base import SapphireEvents

@dataclass
class TaskData:
	name: str
	info: str
	args: list[str]
	func: Callable[[list[str], SapphireEvents.Chain], str]

@dataclass 
class TaskNamespace:
	module: str
	tasks: dict[str, TaskData] = field(default_factory = dict)
	