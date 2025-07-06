
import socket, json, threading, queue
from sapphire.core.base import SapphireEvents
from typing import Tuple
from dataclasses import asdict


class SapphireClient():
	"""
	Base class for connecting with the server.
	"""

	HOST = "127.0.0.1"
	PORT = 6240

	def __init__(self) -> None:
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		self.lock = threading.Lock()
		self.read_thread = threading.Thread(target= self.read)
		self.write_thread = threading.Thread(target = self.write)

		self.is_running = True

		#output from the pov of the server, the string is the error in case something goes wrong
		self.in_buffer: queue.Queue[SapphireEvents.OutputEvent] = queue.Queue()

		self.out_buffer: queue.Queue[SapphireEvents.InputEvent] = queue.Queue()
		

	def start(self):
		self.socket.settimeout(1)
		
		try:
			self.socket.connect((self.HOST, self.PORT))
		except ConnectionRefusedError as e:
			raise e
		
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
		
		return (True, "Success")
	

	def to_output_event(self, parsed_json: dict) -> SapphireEvents.OutputEvent | None:
		try:
			output_event = SapphireEvents.OutputEvent(**parsed_json)
			return output_event
		except KeyError as e:
			self.add_error_event(
				"Server send a invalid json schema. " \
				f"Encountered Error = {e.__class__.__name__}: {e.__str__()}."
			)


	def parse_json(self, json_str: str) -> dict | None:
		try:
			return(json.loads(json_str))
		except json.JSONDecodeError as e:
			self.add_error_event(
				"Client could not parse the json string sent by the server. " \
				f"Encountered Error= {e.__class__.__name__}: {e.__str__()}."
			)


	def from_input_event(self, event: SapphireEvents.InputEvent) ->  str:
		dict_form = asdict(event)
		string = json.dumps(dict_form)
		return string

	def add_error_event(self, msg):
		event = SapphireEvents.OutputEvent(
			"sapphire-client",
			SapphireEvents.make_timestamp(),
			0,
			"error",
			msg,
			False
		)
		self.in_buffer.put(event)

	def read(self):
		
		while self.is_running:

			try:
				data = self.socket.recv(1024)
			except socket.timeout:
				continue
			except ConnectionRefusedError:
				data = None
			
			if not data:
				self.add_error_event(
					"Could not communicate with server. Perhaps it was shutdown?"
				)
				continue
				
			parsed_json = self.parse_json(data.decode())

			if parsed_json is None: continue

			event = self.to_output_event(parsed_json)
			if event: self.in_buffer.put(event)
			
			
	def write(self):
		
		while self.is_running:
			
			try:
				event = self.out_buffer.get(True, 0.5)
			except queue.Empty:
				continue

			payload = self.from_input_event(event)
			
			if payload is None: continue

			try:
				self.socket.sendall(payload.encode())
			except (BrokenPipeError, ConnectionResetError, OSError) as e:
				self.add_error_event("Could not send output event to client. " \
				f"Encountered Error= {e.__class__.__name__}: {e.__str__()}. ")
				
				


			
		