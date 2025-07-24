
import socket, threading, queue, json, select, math
from dataclasses import asdict
from collections.abc import Callable
from typing import Tuple

from sapphire.core.base import (
	SapphireModule, 
	SapphireConfig, 
	SapphireEvents, 
	SapphireCommand
)


class SapphireServer(SapphireModule):

	HOST = "127.0.0.1"
	PORT = 6240

	def __init__(
		self, 
		emit_event: Callable[[SapphireEvents.Event], None], 
		config: SapphireConfig
		) -> None:

		super().__init__(emit_event, config)
		self.has_commands = True
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# map of chain id to client
		self.clients: dict[int, socket.socket] = {}

		self.is_running = True

		try:
			self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.socket.bind((SapphireServer.HOST, SapphireServer.PORT))
		except Exception as e:
			raise Exception("Critical: Could not start sapphire server.") from e
		

		self.out_buffer: queue.Queue[SapphireEvents.Event] = queue.Queue()

		self.lock = threading.Lock()
		self.read_thread = threading.Thread(target = self.read)
		self.write_thread = threading.Thread(target = self.write)

	
	@classmethod
	def name(cls):
		return "server"
	
	def start(self):

		self.socket.settimeout(0.5)
		self.socket.listen()
		self.read_thread.start()
		self.write_thread.start()


	def end(self) -> Tuple[bool, str]:

		self.is_running = False
		self.read_thread.join(8)
		self.write_thread.join(8)

		read_alive = self.read_thread.is_alive()
		write_alive = self.write_thread.is_alive()
		
		self.socket.shutdown(socket.SHUT_WR)

		if read_alive or write_alive:
			return (
				False,
				"Could not close the read and write threads. " \
				f"Read thread = alive: {read_alive}, " \
				f"Write thread = alive: {write_alive}"
		    )
		
		return (True, "")
	

	def handled_events(self) -> list[type[SapphireEvents.Event]]:
		return [
			SapphireEvents.AIResponseEvent,
			SapphireEvents.CommandExecutedEvent,
			SapphireEvents.ConfirmationEvent,
			SapphireEvents.ErrorEvent,
			SapphireEvents.ClientActivationEvent
		]
	

	def handle(self, event: SapphireEvents.Event) -> None:
		match event:
			case SapphireEvents.Event():
				self.out_buffer.put(event)
	

	@SapphireCommand("address", "Get the socket address of the sapphire server.")
	def get_address(self, args: list[str], chain: SapphireEvents.Chain) -> str:
		return f"{self.HOST}:{self.PORT}"


	def serialize_event(self, event: SapphireEvents.Event) -> str:
		dict_form = {}

		dict_form["type"] = event.__class__.__name__
		dict_form["payload"] = asdict(event)

		string_form = json.dumps(dict_form)
		return string_form


	def parse_json(self, json_str: str) -> dict | None:
		try:
			return(json.loads(json_str))
		except json.JSONDecodeError as e:
			error_msg = "Server could not parse the json string sent by a client." \
			f"Encountered Error= {e.__class__.__name__}: {e.__str__()}."

		self.log(
			SapphireEvents.chain(),
			"critical",
			error_msg
		)


	def deserialize_event(self, msg: str) -> SapphireEvents.Event | None:
		d = self.parse_json(msg)

		if not d:
			return None
		
		chain = d["payload"].pop("chain")

		# for some reason dataclasses module doesnt recursively intialize
		# objects from nested dicts so I had to use this primitive method
		# TODO: improve

		try:
			event_type = SapphireEvents.serialize(d["type"])
			event = event_type(
				**d["payload"], chain=SapphireEvents.Chain(chain["context"], chain["flow"])
				)
			return event
		except KeyError as e:
			error_msg = "Server encountered a key error in the input event sent by a client. " \
			f"Encountered Error= {e.__class__.__name__} : {e.__str__()}."

		self.log(
			SapphireEvents.chain(),
			"critical",
			error_msg
		)
		
		
	def handle_client(self, client: socket.socket):
		try:
			with self.lock: data = client.recv(1024)
		except ConnectionResetError:
			data = None

		if not data:
			self.cleanup_client(client)
			return
		
		for msg in data.decode().splitlines():
			event = self.deserialize_event(msg)
			if event:
				self.emit_event(event)


	def greet_client(self, client: socket.socket):

		chain_id = SapphireEvents.new_context_chain()

		event = SapphireEvents.ClientActivationEvent(
			self.name(),
			SapphireEvents.make_timestamp(),
			chain_id,
			f"Client successfully registered to the server with Chain ID: {chain_id}"
		)

		with self.lock:
			self.clients[chain_id.context] = client 

		self.emit_event(event)


	def cleanup_client(self, client: socket.socket):
		client.close()
		for items in self.clients.items():
			if client is items[1]:
				with self.lock: 
					self.clients.pop(items[0])
				break


	def read(self):
		
		while self.is_running:

			try:
				conn, _ = self.socket.accept()
				self.greet_client(conn)
			except socket.timeout:
				pass

			readable: list[socket.socket] = select.select(self.clients.values(), [], [], 0.5)[0]

			for client in readable:
				self.handle_client(client)
					

	def write(self):
		
		while self.is_running:
			
			try:
				event = self.out_buffer.get(True, 0.5)
			except queue.Empty:
				continue


			client = self.clients.get(event.chain.context, None)

			if client is None: continue
			
			payload = self.serialize_event(event)

			try:
				client.sendall(payload.encode())
			except (BrokenPipeError, ConnectionResetError, OSError) as e:
				self.log(
					event.chain,
					"warning",
					"Could not send output event to client. " \
					f"Encountered Error= {e.__class__.__name__}: {e.__str__()}. " \
					f"Client has chain id: {event.chain}" 
				)
				self.cleanup_client(client)


			
			


