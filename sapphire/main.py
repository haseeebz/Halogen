
from sapphire.core import SapphireCore
from sapphire.core.base import SapphireEvents
from sapphire.log import Logger

def main():
	core = SapphireCore()
	core.register_module(Logger)
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