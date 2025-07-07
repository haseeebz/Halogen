from .events import SapphireEvents
from typing import Callable, Literal
import shlex


class SapphireCommands():
	"Class for handling cli commands"

	def __init__(self, emit_event: Callable):
		self.emit_event = emit_event
		self.command_map: dict[str, Callable[[list[str], SapphireEvents.Chain], str]] = {}
		#callable(args: list[str], chain: Chain) -> str

		#first item in the tuple is the name, second is the info
		self.defined_commands: list[tuple[str, str]] = []

		self.define(
			self.help_command,
			"help",
			"Print all available commands."
		)

	def interpret(self, event: SapphireEvents.InputEvent):

		# splitting the command and its args in shell style
		try:
			command = shlex.split(event.message)
			cmd = command[0]
			args = command[1:]
		except (ValueError, IndexError) as e:
			self.log(
				SapphireEvents.chain(event),
				"warning",
				f"Client with chain id '{event.chain}' requested a command but encountered error: " \
				f"({e.__class__.__name__}:{e.__str__()})"
			)

			output_event = SapphireEvents.OutputEvent(
				"command",
				SapphireEvents.make_timestamp(),
				SapphireEvents.chain(event),
				"error",
				f"Invalid Command format. {e.__class__.__name__}:{e.__str__()}"
			)

			self.emit_event(output_event)
			return
		


		# getting the command

		func = self.command_map.get(cmd, None)

		if func is None:
			
			self.log(
				SapphireEvents.chain(event),
				"warning",
				f"Client with chain id '{event.chain}' tried to execute invalid command '{cmd}'"
				)
			
			output_event = SapphireEvents.OutputEvent(
				"command",
				SapphireEvents.make_timestamp(),
				SapphireEvents.chain(event),
				"error",
				f"Undefined Command: {cmd}"
			)

			self.emit_event(output_event)
			return
		

		# executing 

		try:
			msg = func(args, event.chain)
			category = "command"
		except Exception as e:
			msg = f"Failed to execute command. Encountered {e.__class__.__name__}: {e.__str__()}"
			category = "error"

		# output in case of both success and failure

		output_event = SapphireEvents.OutputEvent(
			"command",
			SapphireEvents.make_timestamp(),
			SapphireEvents.chain(event),
			category,
			msg
		)

		self.emit_event(output_event)

		self.log(
			SapphireEvents.chain(event),
			"warning" if category == "error" else "debug",
			f"Client with chain id '{event.chain}' requested command '{cmd}'. " \
			f"Returned Output: {msg if cmd != "help" else '*help-message*'}"  #to not clutter logs
		)
		

	def define(
		self, 
		func: Callable[[list[str], SapphireEvents.Chain], str], 
		cmd: str, 
		info: str
		):

		if cmd in self.command_map.keys():
			raise ValueError(f"Command with name '{cmd}' already defined elsewhere.")
		
		self.command_map[cmd] = func
		self.defined_commands.append((cmd, info))


	def log(self, chain_id: SapphireEvents.Chain, level: Literal["debug", "info", "warning", "critical"], msg: str):
		event = SapphireEvents.LogEvent(
			"command",
			SapphireEvents.make_timestamp(),
			chain_id,
			level,
			msg
		)
		self.emit_event(event)

	_help_str = ""
	def help_command(self, args: list[str], chain: SapphireEvents.Chain) -> str:
		if self._help_str:
			return self._help_str
		
		self._help_str = intro
		for item in self.defined_commands:
			cmd_str = f"{item[0]:<10} : {item[1]}\n"
			self._help_str += cmd_str
			
		return self._help_str

	

intro = """
Welcome to Sapphire! The system designed for modular, configurable, event-driven AI integration with your desktop!
Below is a list of all available commands defined by Sapphire:

"""
