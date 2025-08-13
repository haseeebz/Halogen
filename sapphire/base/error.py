

class SapphireError(Exception):
	"""
	Base class for any sapphire related errors.
	"""
	def __init__(self, *args: object) -> None:
		super().__init__(*args)


