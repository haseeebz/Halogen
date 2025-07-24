from sapphire.core.base import SapphireEvents
from .client import SapphireClient
import socket, shlex

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

	def send_event(self, event: SapphireEvents.Event):
		self.client.out_buffer.put(event)


	def receive_event(self) -> SapphireEvents.Event:
		"Blocks and waits for and event from the server."
		return self.client.in_buffer.get()	


	def check_event(self, timeout : float | None = None) -> SapphireEvents.Event | None:
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
		event = SapphireEvents.UserInputEvent(
			self.name, 
			SapphireEvents.make_timestamp(),
			chain, 
			msg
		)
		self.send_event(event)

		return chain

	def send_command(self, msg: str) -> SapphireEvents.Chain | None:
		"Shorthand for creating a command input event and dispatching it. Blocks for output"

		try:
			command = shlex.split(msg)
			module, cmd = command[0].split("::")
			args = command[1:]
		except (ValueError, IndexError) as e:
			self.client.add_error_event(
				f"Client requested a command but encountered error: " \
				f"({e.__class__.__name__}:{e.__str__()})"
			)
			return None
		
		chain = self.client.chain()
		event = SapphireEvents.CommandEvent(
			self.name, 
			SapphireEvents.make_timestamp(),
			chain,
			module,
			cmd,
			args
		)

		self.send_event(event)
		return chain


	#def send_confirmation(self, msg: str, chain: SapphireEvents.Chain) -> None:
	#	"Send confirmation event and wait for output"
#
#		event = SapphireEvents.ConfirmationEvent(
#			self.name, 
#			SapphireEvents.make_timestamp(),
#			chain, 
#			"confirmation",
#			msg
#		)
#		self.send_event(event) 
	
	
	def end(self):
		self.client.end()

	
	def restart(self):
		self.start()
	