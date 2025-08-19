from .command.handler import HalogenCommandHandler
from .logger.logger   import HalogenLogger
from .model.manager   import HalogenModelManager
from .tasks.manager   import HalogenTaskManager
from .prompt.manager  import HalogenPromptManager
from .server.server   import HalogenServer

from halogen.base.module import HalogenModule
from typing import Type

MODULES: list[Type[HalogenModule]] = [
    HalogenLogger,
    HalogenCommandHandler,
    HalogenServer,
    HalogenModelManager,
    HalogenTaskManager,
    HalogenPromptManager
] 