
from sapphire.core import SapphireCore
from sapphire.core.base import SapphireEvents
from sapphire.logger import Logger

def main():
	core = SapphireCore(__file__)
	core.manager.register_module(Logger)
	core.eventbus.emit(
		SapphireEvents.LogEvent(
			"test",
			SapphireEvents.make_timestamp(),
			"info",
			"Hello World"
		)
	)
	core.run()

main()