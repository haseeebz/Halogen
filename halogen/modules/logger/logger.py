from collections.abc import Callable
from typing import Tuple
from halogen.base import HalogenModule, HalogenEvents, HalogenConfig
import os
from dataclasses import asdict

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
	
LEVELS = {"debug":0, "info":1, "warning":2, "critical":3}

class HalogenLogger(HalogenModule):

	def __init__(self, emit_event: Callable[[HalogenEvents.Event], None], config: HalogenConfig) -> None:
		super().__init__(emit_event, config)
		self.log_file: str
	

	@classmethod
	def name(cls) -> str:
		return "logger"
	

	def start(self) -> None:
		
		path = self.config.get("logfile", "halogen.log")
		if isinstance(path, str):
			self.log_file = path
		self.log(
			HalogenEvents.chain(),
			"info", 
			f"Now logging into file: {os.path.abspath(self.log_file)}"
		)


		self.log_level: str = self.config.get("level", "info")
		if self.log_level not in LEVELS.keys():
			self.log(
				HalogenEvents.chain(),
				"warning",
				f"Invalid log level specified in config.toml '{self.log_level}'. Defaulting to 'info'"
			)
			self.log_level = "info"


		self.to_terminal: bool = self.config.get("terminal", True)


	def handled_events(self) -> list[type[HalogenEvents.Event]]:
		return [
			HalogenEvents.LogEvent,
			HalogenEvents.UserInputEvent
		]
	

	def handle(self, event: HalogenEvents.Event) -> None:
		match event:

			case HalogenEvents.LogEvent():
				if LEVELS[event.level] >= LEVELS[self.log_level]:
					self.file_log(event)
					if self.to_terminal: self.terminal_log(event)

			case HalogenEvents.UserInputEvent():
				pass


	def terminal_log(self, event: HalogenEvents.LogEvent) -> None:

		timestamp = f"[{event.timestamp}]"
		level = Color.colorify(f"[{event.level.upper()}]", Color.level_map[event.level])
		sender = Color.colorify(f"({event.sender})", Color.MAGENTA)
		message = event.message

		log_str = f"{timestamp} {level} {sender} {message}"
		print(log_str)


	def file_log(self, event: HalogenEvents.LogEvent) -> None:

		log_str = f"[{event.timestamp}] [{event.level.upper()}] ({event.sender.capitalize()}) {event.message}\n"

		with open(self.log_file, "a+") as file:
			file.write(log_str)


	def end(self) -> Tuple[bool, str]:
		return (True, "")
			
