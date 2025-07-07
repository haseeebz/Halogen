
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
		self.client_chain: SapphireEvents.Chain = SapphireEvents.Chain(0, 0) #placeholder

		self.lock = threading.Lock()
		self.read_thread = threading.Thread(target= self.read)
		self.write_thread = threading.Thread(target = self.write)

		self.is_running = True
		#output from the pov of the server
		self.in_buffer: queue.Queue[SapphireEvents.OutputEvent] = queue.Queue()

		self.out_buffer: queue.Queue[SapphireEvents.InputEvent] = queue.Queue()
		

	def start(self):
		self.socket.settimeout(1)
		
		try:
			self.socket.connect((self.HOST, self.PORT))
		except (BrokenPipeError, ConnectionResetError, OSError) as e:
			self.add_error_event(
				f"Could not start the client properly! Encountered Error = "\
				f"{e.__class__.__name__}({e.__str__()})"
			)
			
		self.read_thread.start()
		self.write_thread.start()

		event = self.in_buffer.get()

		if event.category == "greeting":
			self.client_chain = event.chain
		else:
			self.add_error_event("No greeting sent by the server :(")


	def end(self):
		self.is_running = False
		self.read_thread.join(8)
		self.write_thread.join(8)
		try:
			self.socket.shutdown(socket.SHUT_WR)
			self.socket.close()
		except (BrokenPipeError, ConnectionResetError, OSError) as e:
			self.add_error_event(
				f"Could not shutdown the client properly! Encountered Error = "\
				f"{e.__class__.__name__}({e.__str__()})"
			)
	

	def chain(self, event: SapphireEvents.Event | None = None) -> SapphireEvents.Chain:
		if isinstance(event, SapphireEvents.Event):
			return event.chain
		else:
			chain = self.client_chain
			self.client_chain = SapphireEvents.Chain(
				self.client_chain.context, 
				self.client_chain.flow + 1
			)
			return chain
			

	def to_output_event(self, parsed_json: dict) -> SapphireEvents.OutputEvent | None:
		d = parsed_json
		try:
			output_event = SapphireEvents.OutputEvent(
				d["sender"],
				d["timestamp"],
				SapphireEvents.Chain(**d["chain"]),
				d["category"],
				d["message"]
				)
			return output_event
		except KeyError as e:
			self.add_error_event(
				"Server send a invalid json schema. " \
				f"Encountered Error = {e.__class__.__name__}({e.__str__()})"
			)


	def parse_json(self, json_str: str) -> dict | None:
		try:
			return(json.loads(json_str))
		except json.JSONDecodeError as e:
			self.add_error_event(
				"Client could not parse the json string sent by the server. " \
				f"Encountered Error= {e.__class__.__name__}({e.__str__()})."
			)


	def from_input_event(self, event: SapphireEvents.InputEvent) ->  str:
		dict_form = asdict(event)
		string = json.dumps(dict_form)
		return string
	

	def add_error_event(self, msg):
		event = SapphireEvents.OutputEvent(
			"sapphire-client",
			SapphireEvents.make_timestamp(),
			self.chain(),
			"error",
			msg
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
					"Could not communicate with server. Perhaps it was shutdown? " 
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
				
			
				


			
		