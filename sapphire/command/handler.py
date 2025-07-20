from sapphire.core.base import SapphireEvents, SapphireModule, SapphireConfig
from typing import Callable, Literal, Tuple
import shlex


# Callable[[list[str], SapphireEvents.Chain], str]

# A function that :
# 1) takes a list of str arguments
# 2) can take a chain object
# 3) and returns a string


class CommandHandler(SapphireModule):
	"Class for handling commands which change the state of sapphire"

	def __init__(self, emit_event: Callable[[SapphireEvents.Event], None], config: SapphireConfig):
		super().__init__(emit_event, config)
		self.command_registry: dict[str, Callable[[list[str], SapphireEvents.Chain], str]]= {}

		#first item in the tuple is the name, second is the info
		self.defined_commands: list[tuple[str, str]] = []

		self.define_command(
			"help",
			self.help_command,
			"Info for all defined commands."
		)

	
	def start(self) -> None:
		pass


	def end(self) -> Tuple[bool, str]:
		return (True, "")


	def handled_events(self) -> list[type[SapphireEvents.Event]]:
		return [
			SapphireEvents.CommandEvent,
			SapphireEvents.CommandRegisterEvent
		]

	@classmethod
	def name(cls):
		return "commands"
		

	def handle(self, event: SapphireEvents.Event) -> None:
		match event:
			case SapphireEvents.CommandEvent():
				self.interpret(event)
			case SapphireEvents.CommandRegisterEvent():
				self.define(event)


	def define(self, event: SapphireEvents.CommandRegisterEvent):
		if event.cmd in self.command_registry.keys():
			raise ValueError()
		
		self.command_registry[event.cmd] = event.func
		self.defined_commands.append((event.cmd, event.info)) 

	# TODO implement command to module map so commands can be deprecated once a module is removed


	def interpret(self, event: SapphireEvents.CommandEvent):

		func = self.command_registry.get(event.cmd, None)

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
