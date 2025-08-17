
def get_model():
	try:
		import google
	except ModuleNotFoundError:
		raise ModuleNotFoundError("Google GenAI package is neccessary for Gemini Model")

	from .gemini import Gemini
	return Gemini