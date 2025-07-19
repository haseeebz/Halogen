from typing import Any, Callable
from sapphire.core.base import SapphireEvents, SapphireModule

# Callable[[SapphireModule, list[str], SapphireEvents.Chain], str]

# A function thats a:
# 1) method of a sapphire module
# 2) takes a list of str arguments
# 3) can take a chain object
# 4) and returns a string


command_registry: dict[str, Callable[[SapphireModule, list[str], SapphireEvents.Chain], str]] = {}

#first item in the tuple is the name, second is the info
defined_commands: list[tuple[str, str]] = []

def command(cmd: str, info: str):

	if cmd in command_registry:
			raise ValueError(f"Command '{cmd}' already defined elsewhere.")

	def deco(func: Callable[[SapphireModule, list[str], SapphireEvents.Chain], str]):
		command_registry[cmd] = func
		defined_commands.append((cmd, info))

		def wrapper(*args, **kwargs):
			return func(*args, **kwargs)
		return wrapper
	
	return deco