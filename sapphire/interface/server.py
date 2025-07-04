
import socket, threading
from collections.abc import Callable
from typing import Tuple
from sapphire.core.base import SapphireModule, SapphireConfig, Event


class SapphireServer(SapphireModule):

	HOST = "127.0.0.1"
	PORT = 6240

	def __init__(self, emit_event: Callable[[Event], None], config: SapphireConfig) -> None:
		super().__init__(emit_event, config)

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.is_running = True
		self.thread = threading.Thread(target = self.run)
		self.lock = threading.Lock()

		try:
			self.socket.bind((SapphireServer.HOST, SapphireServer.PORT))
		except Exception as e:
			raise Exception("Critical: Could not start sapphire server.") from e
	
	@classmethod
	def name(cls):
		return "sapphire-server"
	
	def start(self):
		self.socket.listen()
		self.thread.start()

	def run(self):

		while self.is_running:
			conn, _ = self.socket.accept()

			data = conn.recv(1024)

			if data:
				msg = data.decode()	
				print(f"Received : {msg}")

			conn.sendall(b"Hello World!")

			conn.close()

