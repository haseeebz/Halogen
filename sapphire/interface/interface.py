from sapphire.core.base import SapphireModule, SapphireConfig, SapphireEvents
from .client import SapphireClient

class SapphireInterface():

	def __init__(self, name: str) -> None:
		self.client = SapphireClient()
		self.client.start()
		self.name = name

	def send_command(self, cmd: str, args: list[str]):
		"Shorthand for creating a command event and sending it."
		event = SapphireEvents.CommandEvent(
			self.name,
			SapphireEvents.make_timestamp(),
			0,
			cmd,
			args
		)
		self.client.out_buffer.put(event)

	def send_message(self, msg: str):
		"Shorthand for creating a command event and sending it. This is for user input only."
		event = SapphireEvents.InputEvent(
			self.name, 
			SapphireEvents.make_timestamp(),
			0, 
			"user",
			msg
		)
		self.client.out_buffer.put(event)

	def send_event(self, event: SapphireEvents.InputEvent |)