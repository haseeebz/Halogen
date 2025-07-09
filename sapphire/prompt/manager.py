from collections.abc import Callable
from typing import Tuple
from sapphire.core.base import SapphireModule, SapphireEvents, SapphireConfig
from pathlib import Path
import os

# TODO : improve

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
		#literally just gets the parts/ dir right next to this file
		#relative path won't work here obviously
	
	@classmethod
	def name(cls) -> str:
		return "prompt"
	
	def	start(self) -> None:
		self.assemble_parts()
		

	def handle(self, event: SapphireEvents.Event) -> None:
		match event:

			case SapphireEvents.AIResponseEvent():
				self.memory.append(f"you: {event.message["user"]}")

			case SapphireEvents.InputEvent():
				if event.category != "user": return
				
				prompt = self.make_prompt(event.message)

				prompt_event = SapphireEvents.PromptEvent(
					self.name(),
					SapphireEvents.make_timestamp(),
					SapphireEvents.chain(event),
					prompt
				)

				self.emit_event(prompt_event)


	def handled_events(self) -> list[type[SapphireEvents.Event]]:
		return [
			SapphireEvents.AIResponseEvent,
			SapphireEvents.InputEvent
		]

	
	def end(self) -> Tuple[bool, str]:
		return (True, "")
	

	def assemble_parts(self):
		#assemble all core parts
		for part in os.listdir(self.parts_dir):
			part_path = self.parts_dir / part

			if not part_path.is_file():
				continue

			with open(part_path) as file:
				part_content = file.read()

			if not part_content:
				continue

			part_text = f"\n[{part.upper()}]\n{part_content}"
			
			self.sys_parts.append(part_text)
			

	def make_prompt(self, user_msg: str) -> str:
		
		parts = []
		parts.append("".join(self.sys_parts))

		memory_prompt = f"\n[MEMORY]\n{"\n".join(self.memory)}"
		parts.append(memory_prompt)
		self.memory.append(f"user: {user_msg}")

		user_prompt = f"\n[USER-INPUT]\n{user_msg}"
		parts.append(user_prompt)

		final_prompt = "".join(parts)

		return final_prompt


