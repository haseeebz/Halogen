
import json
from sapphire.base import SapphireEvents, SapphireConfig
from sapphire.modules.model.base import BaseModelProvider, ModelResponse

try:
	from google import genai
	from google.genai import types
except ModuleNotFoundError:
	raise ModuleNotFoundError("Google GenAI package is neccessary for Gemini Model")

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

		self.content_config = types.GenerateContentConfig(
			thinking_config = types.ThinkingConfig(thinking_budget=0),
			response_schema = ModelResponse,
			response_mime_type = "application/json"
		)

		
	@classmethod
	def name(cls) -> str:
		return "gemini"
	

	def generate(self, prompt: SapphireEvents.PromptEvent) -> ModelResponse | None:
		
		response = self.send_request(prompt.content)
		
		if response.parsed is None: 
			return None

		res: BaseModelReponse = response.parsed #type:ignore

		return res
	
		
	def send_request(self, content: str):

		response = self.client.models.generate_content(
			model = "gemini-2.5-flash",
			contents = content,
			config = self.content_config
		)

		return response

