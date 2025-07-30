from collections.abc import Callable
from typing import Tuple
from sapphire.core.base import (
	SapphireEvents,
	SapphireConfig,
	SapphireModule,
	SapphireError,
	SapphireCommand
)

from .meta import TaskNamespace, TaskData


class TaskManager(SapphireModule):

	def __init__(
		self, 
		emit_event: Callable[[SapphireEvents.Event], None], 
		config: SapphireConfig
		) -> None:
	
		super().__init__(emit_event, config)
		self.namespaces: dict[str, TaskNamespace] = {}
		
	
	@classmethod
	def name(cls) -> str:
		return "tasks"
	

	def start(self) -> None:
		pass


	def end(self) -> Tuple[bool, str]:
		return (True, "")
	

	def handled_events(self) -> list[type[SapphireEvents.Event]]:
		return [
			SapphireEvents.TaskEvent,
			SapphireEvents.TaskRegisterEvent
		]
	

	def handle(self, event: SapphireEvents.Event) -> None:
		match event:
			case SapphireEvents.TaskRegisterEvent():
				self.register_task(event)
			case SapphireEvents.TaskEvent():
				pass


	def register_task(self, ev: SapphireEvents.TaskRegisterEvent):

		namespace = self.namespaces.setdefault(
			ev.module,
			TaskNamespace(ev.module)
		)

		if ev.name in namespace.tasks.keys():
			self.log(
				SapphireEvents.chain(ev),
				"warning",
				f"Task with name '{ev.name}' for module '{ev.module}' already registered"
			)
			return
		
		task_data = TaskData(
			ev.name,
			ev.info,
			ev.args,
			ev.func
		)

		namespace.tasks[ev.name] = task_data

		self.log(
			SapphireEvents.chain(ev),
			"info",
			f"Registered task {ev.module}::{ev.name}"
		)
	


	