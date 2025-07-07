from sapphire.interface import SapphireInterface
from sapphire.core.base import SapphireEvents
import sys

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
	

def print_event(event: SapphireEvents.OutputEvent):
	match event.category:
		case "user" | "confirmation":
			print(event.message)
		case "command":
			print(Color.colorify(event.message, Color.CYAN))
		case "error":
			print(Color.colorify(event.message, Color.RED))
		
	
def main():
	interface = SapphireInterface("sapphire-ctl")

	print(Color.colorify("< Sapphire Interface >", Color.BLUE))

	print(
		"Ask your AI something! For commands, use '/'. For available commands, use '/help'. " \
		"Enter '/quit' to exit the interface."
	)

	run = True
	while run:
		user_input = input(">> ")

		if user_input.startswith("/"):
			cmd = user_input.strip().removeprefix("/")

			if cmd in ("quit", "shutdown"):
				run = False

			interface.send_command(cmd)
		else:
			interface.send_message(user_input)
		output = interface.receive_event()
		print_event(output)

	interface.end()
	