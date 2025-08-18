from sapphire.base import SapphireError



class SapphireProviderError(SapphireError):
	"""
	Error to be raised when a provider:

	- Fails to load a model.
	- Is unable to switch a model.
	"""
	def __init__(self, *args: object):
		super().__init__(*args)


class SapphireModelLoadError(SapphireError):
	"""
	Error to be raised when a provider:

	- Fails to load a model.
	- Is unable to switch a model.
	"""
	def __init__(self, *args: object):
		super().__init__(*args)


class SapphireModelResponseError(SapphireError):
	"""
	Error to be raised when a model fails to generate a proper ModelReponse object.
	"""
	def __init__(self, *args: object):
		super().__init__(*args)

	
class SapphireModelApiError(SapphireError):
	"""
	Error to be raised by a model provider when it fails to load an API KEY from the config or file.
	"""
	def __init__(self, *args: object):
		super().__init__(*args)