
from sapphire.core.base import SapphireEvents, SapphireConfig
from sapphire.model.base import BaseModelProvider
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
			thinking_config = types.ThinkingConfig(thinking_budget=0)
		)
		

	@classmethod
	def name(cls) -> str:
		return "gemini"
	

	def generate(self, prompt: SapphireEvents.PromptEvent) -> SapphireEvents.AIResponseEvent | None:
		
		response = self.send_request(prompt.content)

		if response.text is None: 
			return None

		fmt_res = json.loads(response.text)

		event = SapphireEvents.AIResponseEvent(
			self.name(),
			SapphireEvents.make_timestamp(),
			SapphireEvents.chain(prompt),
			fmt_res.get("message", ""),
			fmt_res.get("tasks", []),
			fmt_res.get("extras", {})
		)

		return event

		
	def send_request(self, content: str):

		response = self.client.models.generate_content(
			model = "gemini-2.5-flash",
			contents = content,
			config = self.content_config
		)

		return response


		