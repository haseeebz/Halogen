from halogen.base import HalogenEvents, Chain
from .client import HalogenClient
import socket, shlex
from queue import Empty


class HalogenInterface():
	"""
	Helper class for connecting with Halogen. 
	This should be used instead of the raw Halogen Client since it hides the socket and connection
	messes.
	"""

	def __init__(self, name: str) -> None:
		self.name = name


	def start(self) -> Chain:
		"Start the client and the interface. Returns the first client chain (basically an ID)"
		self.client = HalogenClient()
		self.client.start()
		return self.client.client_chain


	def receive_event(self) -> HalogenEvents.Event:
		"Blocks and waits for and event from the server."
		return self.client.in_buffer.get()	


	def check_event(self, timeout : float | None = None) -> HalogenEvents.Event | None:
		"""
		Checks whether there is an event within the duration of the timeout and returns it, else None.
		If timeout is not specified, it does not block.
		"""
		try:
			return self.client.in_buffer.get(
				False, 
				timeout
			)	
		except Empty:
			return None
		
	
	def send_event(self, ev: HalogenEvents.Event):
		"""
		Send an event to the halogen server.
		"""
		self.client.out_buffer.put(ev)


	def send_message(self, msg: str) -> Chain:
		"""
		Shorthand for creating a user input event and sending it.
		Returns chain id of the message
		"""

		chain = self.client.chain()
		event = HalogenEvents.UserInputEvent(
			self.name, 
			HalogenEvents.make_timestamp(),
			chain, 
			msg
		)
		self.send_event(event)

		return chain


	def send_command(self, namespace: str, cmd: str, args: list[str]) -> Chain:
		"Shorthand for creating a command input event and dispatching it."

		chain = self.client.chain()
		event = HalogenEvents.CommandEvent(
			self.name, 
			HalogenEvents.make_timestamp(),
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


	def shutdown_halogen(self):
		"Shorthand for shutdown halogen."
		self.send_command("core", "shutdown", [])



	
	