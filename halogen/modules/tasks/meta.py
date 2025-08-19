from dataclasses import dataclass, field
from typing import Callable
from halogen.base import Chain

@dataclass
class TaskData:
	name: str
	info: str
	args: list[str]
	func: Callable[[list[str], Chain], str]

@dataclass 
class TaskNamespace:
	module: str
	tasks: dict[str, TaskData] = field(default_factory = dict)
	