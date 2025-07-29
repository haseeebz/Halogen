from abc import ABC
from sapphire.core.base import SapphireEvents, SapphireConfig
from pathlib import Path
import os

from .response import ModelResponse

class BaseModelProvider(ABC):

	def __init__(self, config: SapphireConfig) -> None:
		super().__init__()
		self.config = config
	
	
	@classmethod
	def name(cls) -> str:
		"Returns the name of the model. By default, it's the name of the class."
		return cls.__name__
	

	def load(self) -> bool:
		"Setup to load the model. Not needed if model needs no loading."
		return True


	def unload(self) -> bool:
		"Setup to unload the model. Not needed if model needs no unloading."
		return True
		

	def generate(self, prompt: SapphireEvents.PromptEvent) -> ModelResponse | None:
		"""
		Take a prompt event and return a ModelResponse.
		
		The "message" field of the response event should follow a fixed scheme.
		By default, it MUST include a 'user' field. The model class should be implemented with custom
		schema support.

		In case of a failure (e.g. if using an cloud model), return None and log what went wrong.

		Override this method and don't call super().ask
		"""
		raise NotImplementedError(f"ask method of model '{self.name()}'")


	def load_api_key(self) -> str:
		"""
		Load the API key from the config for non-local models.

		The API key should be "model_name.api_key" in the config, which translates to the overall 
		config path of "model.model_name.api_key".

		For convenience, the user can either put the api key directly in the config file OR they can 
		enter a txt file path followed by a "load:" to indicate the api key must be loaded from a file.
		In the case "load:" is used, the path must be a valid txt file path.

		In case anything goes wrong, this method will raise an exception. Ideally, this should be in the 
		.__init__() of the subclass.
		"""
		
		raw_value: str | None = self.config.get("api_key", None)

		if raw_value is None:
			raise ValueError(f"'model.{self.name()}.api_key' as not specified in the config.")
		
		if not raw_value.startswith("load:"):
			return raw_value
		
		path = Path(raw_value.removeprefix("load:"))

		if not path.is_file():
			raise FileNotFoundError(f"{os.path.abspath(path)} is not a file or does not exist!")	
		
		with open(path) as file:
			key = file.read()

		return key

	


