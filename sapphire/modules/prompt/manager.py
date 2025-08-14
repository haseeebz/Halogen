from collections.abc import Callable
from typing import Tuple
from sapphire.base import SapphireModule, SapphireEvents, SapphireConfig, Chain
from pathlib import Path
import os

from .sub_managers.memory import MemoryManager
from .sub_managers.tasks import TasksManager
# TODO Make prompt manager more robust and modular cuz the current approach is literal duct tape


class SapphirePromptManager(SapphireModule):

	def __init__(
		self, 
		emit_event: Callable[[SapphireEvents.Event], None], 
		config: SapphireConfig
		) -> None:
		super().__init__(emit_event, config)
		
		self.core_sections: list[str] = []
		self.memory: MemoryManager = MemoryManager(self.config.get("memory_length", 50))
		self.tasks: TasksManager = TasksManager()

		self.sections_dir = Path(__file__).resolve().parent / "sections"
	

	@property
	def name(self) -> str:
		return "prompt"
	

	def	start(self) -> None:
		self.load_core_sections()
		

	def handle(self, event: SapphireEvents.Event) -> None:
		match event:

			case SapphireEvents.AIResponseEvent():
				self.memory.add("you", event.message)

			case SapphireEvents.UserInputEvent():
				self.handle_user_input(event)

			case SapphireEvents.TaskRegisteredEvent():
				self.tasks.add_task(event)

			case SapphireEvents.TaskCompletionEvent():
				self.handle_task_completion(event)
				

	def handled_events(self) -> list[type[SapphireEvents.Event]]:
		return [
			SapphireEvents.AIResponseEvent,
			SapphireEvents.UserInputEvent,
			SapphireEvents.TaskRegisteredEvent,
			SapphireEvents.TaskEvent,
			SapphireEvents.TaskCompletionEvent
		]

	
	def end(self) -> Tuple[bool, str]:
		return (True, "")
	

	def load_core_sections(self):

		sections = []
		section_paths = list(self.sections_dir.iterdir())
		section_paths.sort()
		
		for section in section_paths:
			
			if not section.is_file():
				continue
			
			sections.append(section.name)

			with open(section) as file:
				section_text = file.read()

			self.core_sections.append(section_text)

		self.log(
			SapphireEvents.chain(),
			"debug",
			f"Assembled core sections: {sections}"
		)


	def make_prompt_parts(self) -> list[str]:
		parts = []
		parts.extend(self.core_sections)
		parts.append(self.memory.stringify())
		parts.append(self.tasks.stringify())
		return parts


	def handle_user_input(self, event: SapphireEvents.UserInputEvent):	

		self.log(
			SapphireEvents.chain(event),
			"info",
			"Received user input. Making prompt."
		)

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

		self.memory.add("user", event.message)


	def handle_task_completion(self, ev: SapphireEvents.TaskCompletionEvent):

		self.log(
			SapphireEvents.chain(ev),
			"info",
			"Received task completion info. Making prompt."
		)

		prompt = self.make_prompt_parts()

		prompt.append("[SAPPHIRE]")
		msg = f"Completed task '{ev.namespace}::{ev.task_name}'. " \
			f"Success = {ev.success}. Output = {ev.output}"
		
		prompt.append(msg)
		self.memory.add("sapphire", msg)
		
		str_prompt = "\n".join(prompt)

		prompt_event = SapphireEvents.PromptEvent(
			self.name(),
			SapphireEvents.make_timestamp(),
			SapphireEvents.chain(ev),
			str_prompt
		)

		self.emit_event(prompt_event)


