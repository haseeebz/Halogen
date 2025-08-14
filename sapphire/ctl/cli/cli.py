from sapphire.ctl.base import SapphireInterface
import argparse

class SapphireCLI():

	def __init__(self):
		self.setup()
		self.interface = SapphireInterface("sapphire.ctl/tui")

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
			type = list,
			nargs = '*'
		)

	