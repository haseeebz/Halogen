from sapphire.modules.server import SapphireInterface
from sapphire.base import SapphireEvents
import argparse


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
	

class SapphireCLI():

	def __init__(self):
		self.setup()
		self.interface = SapphireInterface("sapphire.ctl/cli")

	def setup(self):
		
		self.parser = argparse.ArgumentParser(
			prog = "sapphire-cli",
			usage = "For sending just commands to sapphire.",
		)

		self.parser.add_argument(
			"module", 
			help = "The name of the module which defines the command", 
			type = str
		)

		self.parser.add_argument(
			"command", 
			help = "Command you want to call.", 
			type = str
		)

		self.parser.add_argument(
			"args", 
			help = "Arguments to sent to the command", 
			type = str,
			nargs = '*'
		)


	def run(self):
		cli_args = self.parser.parse_args() 
		self.interface.start()

		self.interface.send_command(
			cli_args.module,
			cli_args.command,
			cli_args.args
		)

		while True:
			event = self.interface.check_event(0.05)

			if isinstance(event, (SapphireEvents.CommandExecutedEvent, SapphireEvents.ErrorEvent)):
				self.handle_event(event)
				self.interface.end()
				break
			else:
				continue
			

	def handle_event(self, ev: SapphireEvents.Event) -> bool:
		match ev:
			case SapphireEvents.CommandExecutedEvent():
				color = Color.GREEN if ev.success else Color.RED
				print(Color.colorify(ev.output, color))
			case SapphireEvents.ErrorEvent():
				ev : SapphireEvents.ErrorEvent
				color = Color.RED 
				print(Color.colorify(ev.error, color))
		