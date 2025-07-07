from abc import ABC
from sapphire.core.base import SapphireEvents


class BaseModel(ABC):

	def __init__(self) -> None:
		super().__init__()
	
	@classmethod
	def name(cls) -> str:
		"Returns the name of the model. By default, it's the name of the class."
		return cls.__name__
	
	def ask(self, prompt: SapphireEvents.PromptEvent) -> SapphireEvents.AIResponseEvent:
		"""
		Take a prompt event and emit a AI response event.
		
		The "message" field of the response event should follow a fixed scheme.
		By default, it MUST include a 'user' field. The model class should be implemented with custom
		schema support.

		Override this method and don't call super().ask
		"""
		raise NotImplementedError(f"ask method of model '{self.name()}'")




