
import socket, json, threading, queue
from halogen.base import HalogenEvents, Chain
from typing import Tuple
from dataclasses import asdict


class HalogenClient():
	"""
	Base class for connecting with the server.
	"""

	HOST = "127.0.0.1"
	PORT = 6240

	def __init__(self) -> None:
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client_chain: Chain = Chain(0, 0) #placeholder

		self.lock = threading.Lock()
		self.read_thread = threading.Thread(target= self.read)
		self.write_thread = threading.Thread(target = self.write)

		self.is_running = True

		self.in_buffer: queue.Queue[HalogenEvents.Event] = queue.Queue()
		self.out_buffer: queue.Queue[HalogenEvents.Event] = queue.Queue()
		

	def start(self):
		self.socket.settimeout(0.1)
		
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

		if isinstance(event, HalogenEvents.ClientActivationEvent):
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
				f"{e.__class__.__name__}({e})"
			)
	

	def chain(self, event: HalogenEvents.Event | None = None) -> Chain:
		if isinstance(event, HalogenEvents.Event):
			return event.chain
		else:
			chain = self.client_chain
			self.client_chain = Chain(
				self.client_chain.context, 
				self.client_chain.flow + 1
			)
			return chain
			

	def serialize_event(self, event: HalogenEvents.Event) -> str:
		dict_form = {}

		dict_form["type"] = event.__class__.__name__
		dict_form["payload"] = asdict(event)

		string_form = json.dumps(dict_form)+"\n"
		return string_form



	def parse_json(self, json_str: str) -> dict | None:
		try:
			return(json.loads(json_str))
		except json.JSONDecodeError as e:
			error_msg = "Client could not parse the json string sent by the server." \
			f"Encountered Error= {e.__class__.__name__}: {e.__str__()}."

		self.add_error_event(error_msg)


	def deserialize_event(self, msg: str) -> HalogenEvents.Event | None:
		d = self.parse_json(msg)

		if not d:
			return None
		
		chain = d["payload"].pop("chain")
		
		try:
			event_type = HalogenEvents.serialize(d["type"])
			event = event_type(
				**d["payload"], chain=Chain(chain["context"], chain["flow"])
				)
			return event
		except KeyError as e:
			error_msg = "Client encountered a key error in the input event sent by the server. " \
			f"Encountered Error= {e.__class__.__name__} : {e.__str__()}."

		self.add_error_event(error_msg)
		

	def parse_server_input(self, msg: str) -> None:
		for part in msg.splitlines():
			event = self.deserialize_event(part)
			if event:
				 self.in_buffer.put(event)
		

	def add_error_event(self, msg):
		event = HalogenEvents.ErrorEvent(
			"halogen-client",
			HalogenEvents.make_timestamp(),
			self.chain(),
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
				
			self.parse_server_input(data.decode())
			
			
	def write(self):
		
		while self.is_running:
			
			try:
				event = self.out_buffer.get(True, 0.1)
			except queue.Empty:
				continue

			payload = self.serialize_event(event)
			
			if payload is None: continue
			try:
				self.socket.sendall(payload.encode())
			except (BrokenPipeError, ConnectionResetError, OSError) as e:
				self.add_error_event("Could not send output event to client. " \
				f"Encountered Error= {e.__class__.__name__}: {e.__str__()}. ")
				
			
				


			
		