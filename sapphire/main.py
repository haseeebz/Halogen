
from sapphire.core import SapphireCore
from sapphire.core.base import SapphireEvents
from sapphire.logger import Logger
from sapphire.interface import SapphireServer

def main():
	core = SapphireCore(__file__)
	core.manager.register_module(Logger)
	core.manager.register_module(SapphireServer)
	core.run()
