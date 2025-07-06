
import socket, threading, queue, json, select
from dataclasses import asdict
from collections.abc import Callable
from typing import Tuple
from sapphire.core.base import SapphireModule, SapphireConfig, SapphireEvents


class SapphireServer(SapphireModule):

	HOST = "127.0.0.1"
	PORT = 6240

	def __init__(
		self, 
		emit_event: Callable[[SapphireEvents.Event], None], 
		config: SapphireConfig
		) -> None:

		super().__init__(emit_event, config)

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


		# map of clients to set of chain ids it started
		self.clients: dict[socket.socket, set[int]] = {}

		self.is_running = True

		try:
			self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.socket.bind((SapphireServer.HOST, SapphireServer.PORT))
		except Exception as e:
			raise Exception("Critical: Could not start sapphire server.") from e
		

		self.out_buffer: queue.Queue[SapphireEvents.OutputEvent] = queue.Queue()

		self.lock = threading.Lock()
		self.read_thread = threading.Thread(target = self.read)
		self.write_thread = threading.Thread(target = self.write)
	
	@classmethod
	def name(cls):
		return "sapphire-server"
	
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
			SapphireEvents.OutputEvent
		]
	

	def handle(self, event: SapphireEvents.Event) -> None:
		match event:
			case SapphireEvents.OutputEvent():
				self.out_buffer.put(event)
	

	def from_output_event(self, event: SapphireEvents.OutputEvent) -> str:
		dict_form = asdict(event)
		string = json.dumps(dict_form)
		return string


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

	def to_input_event(self, parsed_json: dict) -> SapphireEvents.InputEvent | None:

		try:
			input_event = SapphireEvents.InputEvent(**parsed_json)
			return input_event
		except KeyError as e:
			error_msg = "Server encountered a key error in the input event sent by a client. " \
			f"Encountered Error= {e.__class__.__name__}: {e.__str__()}."

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
			parsed_json = self.parse_json(msg)

			if parsed_json is None: return

			event = self.to_input_event(parsed_json)
			if event:
				self.clients[client].add(event.chain_id)
				self.emit_event(event)


	def cleanup_client(self, client: socket.socket):
		client.close()
		with self.lock:
			self.clients.pop(client, None)


	def read(self):
		
		while self.is_running:

			try:
				conn, _ = self.socket.accept()
				self.clients.setdefault(conn, set())
			except socket.timeout:
				pass

			readable: list[socket.socket] = select.select(self.clients.keys(), [], [], 0.5)[0]

			for client in readable:
				self.handle_client(client)
					

	def write(self):
		
		while self.is_running:
			
			try:
				event = self.out_buffer.get(True, 0.5)
			except queue.Empty:
				continue

			rq_client = None

			for client, chain_ids in self.clients.items():
				if event.chain_id in chain_ids:
					rq_client = client

			if rq_client is None: continue
			
			payload = self.from_output_event(event)
			try:
				rq_client.sendall(payload.encode())
			except (BrokenPipeError, ConnectionResetError, OSError) as e:
				self.log(
					event.chain_id,
					"warning",
					"Could not send output event to client. " \
					f"Encountered Error= {e.__class__.__name__}: {e.__str__()}. " \
					f"Client had chain ids: {self.clients[rq_client]}" 
				)
				self.cleanup_client(rq_client)


			
			


