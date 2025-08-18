
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



class Gemini(BaseModelProvider):

	def __init__(self, config: SapphireConfig) -> None:
		super().__init__(config)

		self.api_key = self.load_api_key()

		self.client = genai.Client(api_key = self.api_key)

		self.supported_models = [
			"gemini-2.5-pro",
			"gemini-2.5-flash",
			"gemini-2.5-flash-lite"
		]

		self.default_model = self.config.get("model_name", "gemini-2.5-flash")
		self.current_model = self.default_model
		self.thinking_budget = self.config.get("thinking_budget", 0)

		self.content_config = types.GenerateContentConfig(
			thinking_config = types.ThinkingConfig(thinking_budget=self.thinking_budget),
			response_schema = ModelResponse,
			response_mime_type = "application/json"
		)


	@classmethod
	def name(cls) -> str:
		return "gemini"


	def load(self, model: str | None = None) -> str:
		
		if not model:
			model = self.default_model
		
		if model not in self.supported_models:
			raise SapphireModelLoadError(f"No model found with name '{model}'!")

		self.current_model = model
		return f"Loaded model '{model}'"


	def unload(self) -> str:
		return f"No unloading required."


	def get_available_models(self) -> list[str]:
		return self.supported_models


	def generate(self, prompt: SapphireEvents.PromptEvent) -> ModelResponse:
		
		try:
			response = self.send_request(prompt.content)
		except genai.errors.ClientError as e:
			msg = f"Client Error (Code:{e.code}) {e.message}!"
			raise SapphireModelResponseError(msg)

		res: BaseModelReponse = response.parsed 
		return res
	
		
	def send_request(self, content: str):

		response = self.client.models.generate_content(
			model = self.current_model,
			contents = content,
			config = self.content_config
		)

		return response

