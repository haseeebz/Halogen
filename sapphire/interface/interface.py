from sapphire.core.base import SapphireEvents
from .client import SapphireClient
import socket

class SapphireInterface():

	def __init__(self, name: str) -> None:
		self.client = SapphireClient()
		self.client.start()
		self.name = name

	def send_message(self, msg: str, chain_id: int = 0):
		"Shorthand for creating a input event and sending it. This is for user input only."
		event = SapphireEvents.InputEvent(
			self.name, 
			SapphireEvents.make_timestamp(),
			chain_id, 
			"user",
			msg
		)
		self.client.out_buffer.put(event)

	def send_event(self, event: SapphireEvents.InputEvent):
		self.client.out_buffer.put(event)

	def receive_event(self, timeout : float | None = None) -> SapphireEvents.OutputEvent | None:
		try:
			return self.client.in_buffer.get(True, timeout)	
		except socket.timeout:
			return None
