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

	def interpret(self, event: SapphireEvents.CommandEvent):

		
		func = self.command_map.get(event.cmd, None)

		if func is None:
			
			self.log(
				SapphireEvents.chain(event),
				"warning",
				f"Client with chain id '{event.chain}' tried to execute invalid command '{event.cmd}'"
				)
			
		
			output_event = SapphireEvents.CommandExecutedEvent(
				"commands",
				SapphireEvents.make_timestamp(),
				SapphireEvents.chain(event),
				(event.cmd, event.args),
				False,
				f"Undefined Command: {event.cmd}"
			)

			self.emit_event(output_event)
			return
		

		# executing 

		try:
			msg = func(event.args, event.chain)
			success = True
		except Exception as e:
			msg = f"Failed to execute command. Encountered {e.__class__.__name__}: {e.__str__()}"
			success = False

		# output in case of both success and failure

		execution_event = SapphireEvents.CommandExecutedEvent(
			"commands",
			SapphireEvents.make_timestamp(),
			SapphireEvents.chain(event),
			(event.cmd, event.args),
			success,
			msg
		)

		self.emit_event(execution_event)

		self.log(
			SapphireEvents.chain(event),
			"warning" if not success  else "debug",
			f"Client with chain id '{event.chain}' requested command '{event.cmd}'. " \
			f"Returned Output: {msg if event.cmd != "help" else '*help-message*'}"  #to not clutter logs
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
