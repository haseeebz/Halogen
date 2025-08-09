

class SapphireError(Exception):
	"""
	Base class for any sapphire related errors. These errors are'nt caught at all by
	core and are raised immediatly after force shutdown whether dev mode is on or not.
	"""
	def __init__(self, *args: object) -> None:
		super().__init__(*args)

