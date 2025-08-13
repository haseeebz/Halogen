from sapphire.base import SapphireEvents, SapphireModule, SapphireConfig, SapphireCommand, Chain
from .meta import CommandData, CommandNamespace

from typing import Callable, Literal, Tuple
import shlex



# Callable[[list[str], SapphireEvents.Chain], str]

# A function that :
# 1) takes a list of str arguments
# 2) can take a chain object
# 3) and returns a string


class SapphireCommandHandler(SapphireModule):
	"""
	Class for handling commands which change the state of sapphire.

	All commands are namespaced using module names.
	
	"""
	

	def __init__(self, emit_event: Callable[[SapphireEvents.Event], None], config: SapphireConfig):
		super().__init__(emit_event, config)
		self.namespaces: dict[str, CommandNamespace] = {}
		
		self.has_commands = True # yeah ironic

	
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
		return "command"
		

	def handle(self, event: SapphireEvents.Event) -> None:
		match event:
			case SapphireEvents.CommandEvent():
				self.interpret(event)
			case SapphireEvents.CommandRegisterEvent():
				self.define(event)


	def define(self, ev: SapphireEvents.CommandRegisterEvent):

		namespace = self.namespaces.setdefault(
			ev.module,
			CommandNamespace(ev.module)
		)

		if ev.cmd in namespace.defined:
			raise ValueError()
		
		self.log(
			SapphireEvents.chain(ev),
			"debug",
			f"Registered command: {ev.module}::{ev.cmd} Info : {ev.info}"
		)

		command = CommandData(
			ev.cmd,
			ev.info,
			ev.func
		)


		namespace.commands[ev.cmd] = command
		namespace.defined.add(ev.cmd)


	# TODO implement "module to command" map so commands can be deprecated once a module is removed
	# TODO namespace commands


	def interpret(self, ev: SapphireEvents.CommandEvent):

		namespace = self.namespaces.get(ev.module, None)

		if namespace:
			cmd_data = namespace.commands.get(ev.cmd, None)
		else:
			cmd_data = None

		# TODO make it clear whether the command is not defined or the module namespace.
		
		if cmd_data is None:
			
			self.log(
				SapphireEvents.chain(ev),
				"warning",
				f"Client with chain id '{ev.chain}' tried to execute invalid command {ev.module}::{ev.cmd}"
				)
			
		
			output_event = SapphireEvents.CommandExecutedEvent(
				"commands",
				SapphireEvents.make_timestamp(),
				SapphireEvents.chain(ev),
				(ev.module, ev.cmd, ev.args),
				False,
				f"Undefined Command: {ev.module}::{ev.cmd}"
			)

			self.emit_event(output_event)
			return
		

		# executing 

		try:
			msg = cmd_data.func(ev.args, ev.chain)
			success = True
		except Exception as e:
			msg = f"Failed to execute command. Encountered {e.__class__.__name__}: {e.__str__()}"
			success = False

		# output in case of both success and failure

		execution_event = SapphireEvents.CommandExecutedEvent(
			"commands",
			SapphireEvents.make_timestamp(),
			SapphireEvents.chain(ev),
			(ev.module, ev.cmd, ev.args),
			success,
			msg
		)

		self.emit_event(execution_event)

		self.log(
			SapphireEvents.chain(ev),
			"warning" if not success  else "info",
			f"Client with chain id '{ev.chain}' requested command '{ev.module}::{ev.cmd}'. " \
			f"Returned Output: {msg if ev.cmd != 'help' else '*help-message*'}"  #to not clutter logs
		)
		

	_help_str = ""
	@SapphireCommand("help", "Get info about commands")
	def help_command(self, args: list[str], chain: Chain) -> str:
		
		if self._help_str:
			return self._help_str
		
		temp = []
		
		self._help_str = intro
		for name, namespace in self.namespaces.items():
			for cmd_data in namespace.commands.values():
				temp.append(f"{name:<8}::{cmd_data.cmd:<10} : {cmd_data.info}\n")
			temp.append("\n")
				
		self._help_str += "".join(temp)

		return self._help_str
	
	

	

intro = """
Welcome to Sapphire! The system designed for modular, configurable, event-driven AI integration with your desktop!
Below is a list of all available commands defined by Sapphire:

"""
