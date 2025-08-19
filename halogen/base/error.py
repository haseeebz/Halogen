

class HalogenError(Exception):
	"""
	Base class for any halogen related errors.
	"""
	def __init__(self, *args: object) -> None:
		super().__init__(*args)


