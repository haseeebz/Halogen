from halogen.base import HalogenError

class HalogenTaskError(HalogenError):
	"""
	Error to be raised when a task fails. This error is caught by the task manager and is logged 
	and informed to the model.
	"""

	def __init__(self, *args: object) -> None:
		super().__init__(*args)
