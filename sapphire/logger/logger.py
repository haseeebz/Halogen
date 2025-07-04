from collections.abc import Callable
from typing import Tuple
from sapphire.core.base import SapphireModule, SapphireEvents, Event, SapphireConfig
import os


class Color:
	RESET = "\033[0m"
	RED = "\033[31m"
	GREEN = "\033[32m"
	YELLOW = "\033[33m"
	BLUE = "\033[34m"
	MAGENTA = "\033[35m"
	CYAN = "\033[36m"
	GRAY = "\033[90m"

	@staticmethod
	def colorify(text:str, color):
		return f"{color}{text}{Color.RESET}"
	
	level_map = {
		"debug" : CYAN,
		"info" : GREEN,
		"warning" : YELLOW,
		"critical" : RED
	}
	

class Logger(SapphireModule):

	def __init__(self, emit_event: Callable[[Event], None], config: SapphireConfig) -> None:
		super().__init__(emit_event, config)
		self.log_file: str
	

	@classmethod
	def name(cls) -> str:
		return "logger"
	

	def start(self) -> None:
		path = self.config.get("logfile", "sapphire.log")
		if isinstance(path, str):
			self.log_file = path

		self.log("info", f"Now logging into file: {os.path.abspath(self.log_file)}")


	def handled_events(self) -> list[type[Event]]:
		return [
			SapphireEvents.LogEvent
		]
	

	def handle(self, event: Event) -> None:
		match event:
			case SapphireEvents.LogEvent():
				self.file_log(event)
				self.terminal_log(event)


	def terminal_log(self, event: SapphireEvents.LogEvent) -> None:

		timestamp = f"[{event.timestamp}]"
		level = Color.colorify(f"[{event.level.upper()}]", Color.level_map[event.level])
		sender = Color.colorify(f"({event.sender})", Color.MAGENTA)
		message = event.message

		log_str = f"{timestamp} {level} {sender} {message}"
		print(log_str)


	def file_log(self, event: SapphireEvents.LogEvent) -> None:

		log_str = f"[{event.timestamp}] [{event.level.upper()}] ({event.sender.capitalize()}) {event.message}\n"

		with open(self.log_file, "a+") as file:
			file.write(log_str)


	def end(self) -> Tuple[bool, str]:
		return (True, "")
			
