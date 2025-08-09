from collections.abc import Callable
from typing import Tuple
from sapphire.base import SapphireModule, SapphireEvents, SapphireConfig, Chain
from pathlib import Path
import os

# TODO Make prompt manager more robust and modular cuz the current approach is literal duct tape


class SapphirePromptManager(SapphireModule):

	def __init__(
		self, 
		emit_event: Callable[[SapphireEvents.Event], None], 
		config: SapphireConfig
		) -> None:
		super().__init__(emit_event, config)
		
		self.core_sections: list[str] = []
		self.memory_list: list[str] = []
		self.tasks_namespaces: dict[str, list[tuple[str, str, list[str]]]] = {}
		self.tasks_section_string = ""

		self.sections_dir = Path(__file__).resolve().parent / "sections"
	

	@classmethod
	def name(cls) -> str:
		return "prompt"
	

	def	start(self) -> None:
		self.load_core_sections()
		

	def handle(self, event: SapphireEvents.Event) -> None:
		match event:

			case SapphireEvents.AIResponseEvent():
				self.add_memory("you", event.message)

			case SapphireEvents.UserInputEvent():
				self.handle_user_input(event)

			case SapphireEvents.TaskRegisteredEvent():
				self.add_task(event)
				self.make_task_section()

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
	

	def load_core_sections(self):

		for section in self.sections_dir.iterdir():
			
			if not section.is_file():
				continue

			with open(section) as file:
				section_text = file.read()

			self.core_sections.append(section_text)


	def make_prompt_parts(self) -> list[str]:
		parts = []
		parts.extend(self.core_sections)
		parts.append("[MEMORY]")
		parts.extend(self.memory_list)
		parts.extend(self.tasks_section_string)
		return parts


	def handle_user_input(self, event: SapphireEvents.UserInputEvent):	
		prompt = self.make_prompt_parts()
		prompt.append("[USER]")
		prompt.append(event.message)

		str_prompt = "\n".join(prompt)

		prompt_event = SapphireEvents.PromptEvent(
			self.name(),
			SapphireEvents.make_timestamp(),
			SapphireEvents.chain(event),
			str_prompt
		)

		self.emit_event(prompt_event)

		self.add_memory("user", event.message)


	def handle_task_completion(self, ev: SapphireEvents.TaskCompletionEvent):
		prompt = self.make_prompt()

		prompt.append("[SAPPHIRE]")

		prompt.append(
			f"Completed task '{ev.namespace}::{ev.task_name}'. " \
			f"Success = {ev.success}. Output = {ev.output}"
		)

		str_prompt = "\n".join(prompt)

		prompt_event = SapphireEvents.PromptEvent(
			self.name(),
			SapphireEvents.make_timestamp(),
			SapphireEvents.chain(ev),
			str_prompt
		)

		self.emit_event(prompt_event)


	def add_memory(self, subject: str, msg: str) -> None:
		if len(self.memory_list) > self.config.get("memory_length", 30):
			self.memory_list.pop(0)
			
		self.memory_list.append(f"{subject.capitalize()}: {msg}\n")


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
			
		self.tasks_section_string = "".join(string)
			
		