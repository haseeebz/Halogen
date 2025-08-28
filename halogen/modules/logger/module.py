from collections.abc import Callable
from typing import Tuple
from pathlib import Path
from halogen.base import HalogenModule, HalogenEvents, HalogenConfig
import os
from dataclasses import asdict

from .colors import Color


class HalogenLogModule(HalogenModule):

	def __init__(self, emit_event: Callable[[HalogenEvents.Event], None], config: HalogenConfig) -> None:
		super().__init__(emit_event, config)

		self.log_file: Path

		self.log_colors = {
			"debug" : CYAN,
			"info" : GREEN,
			"warning" : YELLOW,
			"critical" : RED
		}
	
		self.log_levels = {"debug" : 0, "info" : 1, "warning" : 2, "critical" : 3}

	
	@classmethod
	def name(cls) -> str:
		return "logger"


	def start(self) -> None:
		
		path = self.config.get("logfile", "halogen.log")

		if isinstance(path, str):
			self.log_file = Path(path)

		self.log(
			HalogenEvents.chain(),
			"info", 
			f"Now logging into file: {self.log_file.absolute()}"
		)

		self.current_level: str = self.config.get("level", "info")

		if self.current_level not in self.log_levels.keys():

			self.log(
				HalogenEvents.chain(),
				"warning",
				f"Invalid log level specified in config.toml '{self.current_level}'. Defaulting to 'info'"
			)
			self.current_level = "info"

		self.to_terminal: bool = self.config.get("terminal", True)


	def end(self) -> Tuple[bool, str]:
		return (True, "")


	def handled_events(self) -> list[type[HalogenEvents.Event]]:
		return [
			HalogenEvents.LogEvent
		]
	

	def handle(self, ev: HalogenEvents.Event) -> None:
		match ev:

			case HalogenEvents.LogEvent():
				self.write_log(ev)
				

	def write_log(self, ev: HalogenEvents.LogEvent) -> None:
		if self.log_levels[ev.level] >= self.log_levels[self.current_level]:
			self.file_log(ev)
			if self.to_terminal: self.terminal_log(ev)

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


	
			
