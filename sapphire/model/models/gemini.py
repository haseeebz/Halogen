
from sapphire.core.base import SapphireEvents, SapphireConfig
from sapphire.model.base import BaseModelProvider, ModelResponse
import json



class Gemini(BaseModelProvider):

	def __init__(self, config: SapphireConfig) -> None:
		super().__init__(config)

		from google import genai
		from google.genai import types
		
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


		