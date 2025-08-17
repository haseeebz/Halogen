from sapphire.base import SapphireError

class SapphireModelLoadError(SapphireError):
	"""
	Error to be raised when a provider:

	- Fails to load a model.
	- Is unable to switch a model.
	"""
	def __init__(self, *args: obj):
		super.__init__(*args)


class SapphireModelResponseError(SapphireError):
	"""
	Error to be raised when a model fails to generate a proper ModelReponse object.
	"""
	def __init__(self, *args: obj):
		super.__init__(*args)