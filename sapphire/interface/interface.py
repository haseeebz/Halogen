from sapphire.core.base import SapphireEvents
from .client import SapphireClient
import socket, shlex

class SapphireInterface():
	"""
	Helper class for connecting with Sapphire. Abstracts away SapphireClient.
	"""

	def __init__(self, name: str) -> None:
		self.name = name


	def start(self) -> None:
		"Start the client and the interface."
		self.client = SapphireClient()
		self.client.start()


	def receive_event(self) -> SapphireEvents.Event:
		"Blocks and waits for and event from the server."
		return self.client.in_buffer.get()	


	def check_event(self, timeout : float | None = None) -> SapphireEvents.Event | None:
		"""
		Checks whether there is an event within the duration of the timeout and returns it, else None.
		If timeout is not specified, it does not block.
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
		Returns chain id of the message
		"""

		chain = self.client.chain()
		event = SapphireEvents.UserInputEvent(
			self.name, 
			SapphireEvents.make_timestamp(),
			chain, 
			msg
		)
		self.send_event(event)

		return chain


	def send_command(self, namespace: str, cmd: str, args: list[str]) -> SapphireEvents.Chain:
		"Shorthand for creating a command input event and dispatching it."

		chain = self.client.chain()
		event = SapphireEvents.CommandEvent(
			self.name, 
			SapphireEvents.make_timestamp(),
			chain,
			namespace,
			cmd,
			args
		)

		self.send_event(event)
		return chain


	def end(self):
		self.client.end()


	def restart(self):
		self.client.end()
		self.start()


	def shutdown_sapphire(self):
		"Shorthand for shutdown sapphire."
		self.send_command("core", "shutdown", [])



	
	