
import json
from sapphire.base import SapphireEvents, SapphireConfig
from sapphire.modules.model.base import (
	ModelResponse,
	BaseModelProvider,
	SapphireModelLoadError,
	SapphireModelResponseError
)

from google import genai
from google.genai import types

# TODO
# Thinking budget in config + default model in config
# Supporting more models than just the flash
# Allowing it to change models using commands that model class will potentially define
# Maybe notifying when the model runs out of tokens?
# Error proning it
# Not specific to gemini but add some way for it to log what went wrong


class Gemini(BaseModelProvider):

	def __init__(self, config: SapphireConfig) -> None:
		super().__init__(config)

		self.api_key = self.load_api_key()

		self.client = genai.Client(
			api_key = self.api_key
		)

		self.supported_models = {
			"gemini-2.5-pro",
			"gemini-2.5-flash",
			"gemini-2.5-flash-lite"
		}

		self.thinking_budget = self.config.get("thinking_budget", 0)
		self.model_name = self.config.get("model_name", "gemini-2.5-flash")

		self.content_config = types.GenerateContentConfig(
			thinking_config = types.ThinkingConfig(thinking_budget=self.thinking_budget),
			response_schema = ModelResponse,
			response_mime_type = "application/json"
		)


	@classmethod
	def name(cls) -> str:
		return "gemini"


	def load(self) -> tuple[bool, str]:
		return (True, "No loading action needed.")


	def unload(self) -> tuple[bool, str]:
		return (True, "No unloading action needed.")


	def switch_model(self, name: str) -> tuple[bool, str]:
		
		if name not in self.supported_models:
			return (False, f"Unknown model: {name}")

		self.model_name = name

		return (True, f"Successfully switched model to {name}.")


	def get_available_models(self) -> set[str]:
		return self.supported_models


	def generate(self, prompt: SapphireEvents.PromptEvent) -> ModelResponse:
		
		
		try:
			response = self.send_request(prompt.content)
		except genai.errors.ClientError as e:
			msg = f"Client Error (Code:{e.code}) {e.message}!"
			raise SapphireModelResponseError(msg)

		if response.parsed is None: 
			return None

		res: BaseModelReponse = response.parsed #type:ignore

		return res
	
		
	def send_request(self, content: str):

		response = self.client.models.generate_content(
			model = self.model_name,
			contents = content,
			config = self.content_config
		)

		return response

