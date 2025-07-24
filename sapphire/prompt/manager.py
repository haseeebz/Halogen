from collections.abc import Callable
from typing import Tuple
from sapphire.core.base import SapphireModule, SapphireEvents, SapphireConfig
from pathlib import Path
import os


class PromptManager(SapphireModule):

	def __init__(
		self, 
		emit_event: Callable[[SapphireEvents.Event], None], 
		config: SapphireConfig
		) -> None:
		super().__init__(emit_event, config)
		
		self.sys_parts: list[str] = [] 
		self.memory: list[str] = []

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
				


	def handled_events(self) -> list[type[SapphireEvents.Event]]:
		return [
			SapphireEvents.AIResponseEvent,
			SapphireEvents.UserInputEvent
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

			part_text = f"\n[{part.removesuffix(".txt").upper()}]\n{part_content}"
			
			self.sys_parts.append(part_text)


	def handle_user_input(self, event: SapphireEvents.UserInputEvent):	
		prompt = self.make_prompt(event.message)

		prompt_event = SapphireEvents.PromptEvent(
			self.name(),
			SapphireEvents.make_timestamp(),
			SapphireEvents.chain(event),
			prompt
		)

		self.emit_event(prompt_event)


	def make_prompt(self, user_msg: str) -> str:
		
		parts = []
		parts.append("".join(self.sys_parts))

		memory_prompt = f"\n[MEMORY]\n{"\n".join(self.memory)}"
		parts.append(memory_prompt)

		user_prompt = f"\n[USER-INPUT]\n{user_msg}"
		parts.append(user_prompt)

		final_prompt = "".join(parts)

		self.add_memory("user", user_msg)

		return final_prompt


	def add_memory(self, subject: str, msg: str) -> None:
		if len(self.memory) > self.config.get("memory_length", 30):
			self.memory.pop(0)
			
		self.memory.append(f"{subject.capitalize()}: {msg}")
