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
				self.exec_task(event)                                    



	def register_task(self, ev: SapphireEvents.TaskRegisterEvent):

		namespace = self.namespaces.setdefault(
			ev.namespace,
			TaskNamespace(ev.namespace)
		)

		if ev.task_name in namespace.tasks.keys():
			self.log(
				SapphireEvents.chain(ev),
				"warning",
				f"Task with name '{ev.task_name}' for namespace '{ev.namespace}' already registered"
			)
			return
		
		task_data = TaskData(
			ev.task_name,
			ev.info,
			ev.args_info,
			ev.func
		)

		namespace.tasks[ev.task_name] = task_data

		self.log(
			SapphireEvents.chain(ev),
			"debug",
			f"Registered task {ev.namespace}::{ev.task_name}"
		)

		registered_ev = SapphireEvents.TaskRegisteredEvent(
			self.name(),
			SapphireEvents.make_timestamp(),
			SapphireEvents.chain(ev),
			ev.namespace,
			ev.task_name,
			ev.args_info,
			ev.info
		)

		self.emit_event(registered_ev)

	

	def exec_task(self, ev: SapphireEvents.TaskEvent):

		self.log(
			SapphireEvents.chain(ev),
			"debug",
			f"Executing task {ev.chain} {ev.namespace}::{ev.task_name} with args {ev.args}"
		)
		
		namespace = self.namespaces.setdefault(
			ev.namespace,
			TaskNamespace(ev.namespace)
		)

		if ev.task_name not in namespace.tasks.keys():
			self.log(
				SapphireEvents.chain(ev),
				"warning",
				f"Task with name '{ev.task_name}' for namespace '{ev.namespace}' not found."
			)
			return

		func = namespace.tasks[ev.task_name].func

		try:
			output = func(ev.args, ev.chain)
			success = True
		except Exception as e:
			output = f"{e.__class__.__name__}: {str(e)}"
			success = False


		output_event = SapphireEvents.TaskCompletionEvent(
			self.name(),
			SapphireEvents.make_timestamp(),
			SapphireEvents.chain(ev),
			ev.namespace,
			ev.task_name,
			ev.args,
			success,
			output
		)

		self.emit_event(output_event)

		self.log(
			SapphireEvents.chain(ev),
			"info",
			f"Executed task {ev.chain} {ev.namespace}::{ev.task_name}. Success = {success}"
		)

		self.log(
			SapphireEvents.chain(ev),
			"debug" if success else "warning",
			f"Executed task {ev.chain} {ev.namespace}::{ev.task_name} returned {output}"
		)


	
	