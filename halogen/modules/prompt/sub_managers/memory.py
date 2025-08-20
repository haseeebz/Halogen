

memory_intro = """
[MEMORY]
Previous chat history between the user, you and halogen.

"""

class MemoryManager():

	def __init__(self, limit: str):
		self.storage: list[str] = []
		self.limit = limit
	
	def add(self, subject: str, msg: str):
		if len(self.storage) > self.limit:
			self.storage.pop(0)

		mem = f"({subject}) : {msg}"

		self.storage.append(mem)

	def stringify(self) -> str:
		return memory_intro + "\n".join(self.storage)
