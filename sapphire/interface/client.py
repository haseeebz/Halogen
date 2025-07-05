
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

		#output from the pov of the server, the string is the error in case something goes wrong
		self.in_buffer: queue.Queue[SapphireEvents.OutputEvent|str] = queue.Queue()

		self.out_buffer: queue.Queue[
			SapphireEvents.CommandEvent|
			SapphireEvents.InputEvent
			] = queue.Queue()
		

	def start(self):
		self.socket.settimeout(1)
		self.socket.bind((self.HOST, self.PORT))
		self.read_thread.start()
		self.write_thread.start()


	def end(self) -> Tuple[bool, str]:
		self.is_running = False
		self.read_thread.join(8)
		self.write_thread.join(8)

		read_alive = self.read_thread.is_alive()
		write_alive = self.write_thread.is_alive()

		if read_alive or write_alive:
			return (
				False,
				"Could not close the read and write threads. " \
				f"Read thread = alive: {read_alive}, " \
				f"Write thread = alive: {write_alive}"
		    )
		
		return (True, "Success")
	

	def to_output_event(self, parsed_json: dict) -> SapphireEvents.OutputEvent | str:
		try:
			output_event = SapphireEvents.OutputEvent(**parsed_json["payload"])
			return output_event
		except KeyError:
			error_msg = "Server send a invalid json schema."
			return error_msg


	def parse_json(self, json_str: str) -> dict | str:
		try:
			return(json.loads(json_str))
		except json.JSONDecodeError:
			error_msg = "Client could not parse the json string sent by the server."
			return error_msg


	def from_event(self, event: SapphireEvents.Event) -> str | None:

		match event:
			case SapphireEvents.CommandEvent():
				return self.from_command_event(event)
			case SapphireEvents.InputEvent():
				return self.from_input_event(event)


	def from_input_event(self, event: SapphireEvents.InputEvent) ->  str:
		dict_form = asdict(event)
		string = json.dumps(dict_form)
		return string


	def from_command_event(self,  event: SapphireEvents.CommandEvent) ->  str:
		dict_form = asdict(event)
		string = json.dumps(dict_form)
		return string


	def read(self):
		
		while self.is_running:

			try:
				data = self.socket.recv(1024)
			except socket.timeout:
				continue

			parsed_json = self.parse_json(data.decode())

			if isinstance(parsed_json, str):
				self.in_buffer.put(parsed_json)
				continue

			event = self.to_output_event(parsed_json)
			self.in_buffer.put(event)
			
			
	def write(self):
		
		while self.is_running:
			
			try:
				event = self.out_buffer.get(True, 0.5)
			except queue.Empty:
				continue

			payload = self.from_event(event)
			
			if payload is None: continue

			try:
				self.socket.sendall(payload.encode())
			except (BrokenPipeError, ConnectionResetError, OSError) as e:
				error_msg = "Could not send output event to client. " \
				f"Encountered Error= {e.__class__.__name__}: {e.__str__}. "
				self.in_buffer.put(error_msg)
				
				


			
		