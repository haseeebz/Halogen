from .command.handler import SapphireCommandHandler
from .logger.logger   import SapphireLogger
from .model.manager   import SapphireModelManager
from .tasks.manager   import SapphireTaskManager
from .prompt.manager  import SapphirePromptManager
from .server.server   import SapphireServer

from sapphire.base.module import SapphireModule
from typing import Type

MODULES: list[Type[SapphireModule]] = [
    SapphireLogger,
    SapphireCommandHandler,
    SapphireServer,
    SapphireModelManager,
    SapphireTaskManager,
    SapphirePromptManager
] 