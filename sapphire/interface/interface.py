from sapphire.core.base import SapphireEvents
from .client import SapphireClient
import socket

class SapphireInterface():
	"""
	Helper class for connecting with Sapphire. Abstracts away SapphireClient.
	"""

	def __init__(self, name: str) -> None:
		self.start()
		self.name = name

	def start(self) -> None:
		self.client = SapphireClient()
		self.client.start()

	def send_event(self, event: SapphireEvents.InputEvent):
		self.client.out_buffer.put(event)


	def receive_event(self) -> SapphireEvents.OutputEvent:
		"Blocks and waits for and event from the server."
		return self.client.in_buffer.get()	


	def check_event(self, timeout : float | None = None) -> SapphireEvents.OutputEvent | None:
		"""
		Checks whether there is an event within the duration of the timeout and returns it, else None.
		If timeout is not specified, it does not block and returns an 
		"""
		try:
			return self.client.in_buffer.get(
				True if timeout else False, 
				timeout
			)	
		except socket.timeout:
			return None
		

	def send_message(self, msg: str) -> SapphireEvents.Chain:
		"""
		Shorthand for creating a user input event and sending it.
		Returns sub-chain id of the message
		"""

		chain = self.client.chain()
		event = SapphireEvents.InputEvent(
			self.name, 
			SapphireEvents.make_timestamp(),
			chain, 
			"user",
			msg
		)
		self.send_event(event)

		return chain

	def send_command(self, cmd: str) -> SapphireEvents.Chain:
		"Shorthand for creating a command input event and dispatching it. Blocks for output"

		chain = self.client.chain()
		event = SapphireEvents.InputEvent(
			self.name, 
			SapphireEvents.make_timestamp(),
			chain,
			"command",
			cmd
		)
		self.send_event(event)

		return chain


	def send_confirmation(self, msg: str, chain: SapphireEvents.Chain) -> None:
		"Send confirmation event and wait for output"

		event = SapphireEvents.InputEvent(
			self.name, 
			SapphireEvents.make_timestamp(),
			chain, 
			"confirmation",
			msg
		)
		self.send_event(event) 
	
	
	def end(self):
		self.client.end()

	
	def restart(self):
		self.start()
	