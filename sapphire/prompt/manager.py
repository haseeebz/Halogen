from collections.abc import Callable
from typing import Tuple
from sapphire.core.base import SapphireModule, SapphireEvents, SapphireConfig
from pathlib import Path
import os

# TODO Make prompt manager more robust and modular cuz the current approach is literal duct tape


class PromptManager(SapphireModule):

	def __init__(
		self, 
		emit_event: Callable[[SapphireEvents.Event], None], 
		config: SapphireConfig
		) -> None:
		super().__init__(emit_event, config)
		
		self.sys_parts: list[str] = [] 
		self.memory: list[str] = []
		self.tasks_namespaces: dict[str, list[tuple[str, str, list[str]]]] = {}

		self.parts_dir = Path(__file__).resolve().parent / "parts"
	

	@classmethod
	def name(cls) -> str:
		return "prompt"
	

	def	start(self) -> None:
		self.assemble_parts()
		

	def handle(self, event: SapphireEvents.Event) -> None:
		match event:

			case SapphireEvents.AIResponseEvent():
				self.add_memory("you", event.message)

			case SapphireEvents.UserInputEvent():
				self.handle_user_input(event)

			case SapphireEvents.TaskRegisteredEvent():
				self.add_task(event)

			case SapphireEvents.TaskCompletionEvent():
				self.handle_task_completion(event)
				


	def handled_events(self) -> list[type[SapphireEvents.Event]]:
		return [
			SapphireEvents.AIResponseEvent,
			SapphireEvents.UserInputEvent,
			SapphireEvents.TaskRegisteredEvent,
			SapphireEvents.TaskCompletionEvent
		]

	
	def end(self) -> Tuple[bool, str]:
		return (True, "")
	

	def assemble_parts(self):

		for part in os.listdir(self.parts_dir):
			part_path = self.parts_dir / part

			if not part_path.is_file():
				continue

			with open(part_path) as file:
				part_content = file.read()

			if not part_content:
				continue

			part_text = f"\n[{part.removesuffix('.txt').upper()}]\n{part_content}"
			
			self.sys_parts.append(part_text)


	def handle_user_input(self, event: SapphireEvents.UserInputEvent):	
		prompt = self.make_prompt()

		prompt.append("\n[USER]\n")
		prompt.append(event.message)

		self.add_memory("user", event.message)

		str_prompt = "".join(prompt)

		prompt_event = SapphireEvents.PromptEvent(
			self.name(),
			SapphireEvents.make_timestamp(),
			SapphireEvents.chain(event),
			str_prompt
		)

		self.emit_event(prompt_event)


	def handle_task_completion(self, ev: SapphireEvents.TaskCompletionEvent):
		prompt = self.make_prompt()

		prompt.append("\n[SAPPHIRE]\n")

		prompt.append(
			f"Completed task '{ev.namespace}::{ev.task_name}'. " \
			f"Success = {ev.success}. Output = {ev.output}"
		)

		str_prompt = "".join(prompt)

		prompt_event = SapphireEvents.PromptEvent(
			self.name(),
			SapphireEvents.make_timestamp(),
			SapphireEvents.chain(ev),
			str_prompt
		)

		self.emit_event(prompt_event)


	def make_prompt(self) -> list[str]:
		
		parts = []
		parts.extend(self.sys_parts)
		parts.append("\n[MEMORY]\n")
		parts.extend(self.memory)
		parts.extend(self.make_task_section())
		return parts


	def add_memory(self, subject: str, msg: str) -> None:
		if len(self.memory) > self.config.get("memory_length", 30):
			self.memory.pop(0)
			
		self.memory.append(f"{subject.capitalize()}: {msg}\n")


	def add_task(self, ev: SapphireEvents.TaskRegisteredEvent):
		
		task_list = self.tasks_namespaces.setdefault(ev.namespace, [])
		data = (ev.task_name, ev.info, ev.args_info)
		task_list.append(data)


	def make_task_section(self):
		string = []
		string.append("\n[TASKS AVAILABLE]\nAll available tasks that you can do.\n")
		for ns, taskslist in self.tasks_namespaces.items():
			string.append(f"\nNamespace: '{ns}'\nDefined Tasks:\n")
			for n, i, a in taskslist:
				string.append(f"{n}({a}) : {i}")
			
		return string
			
		