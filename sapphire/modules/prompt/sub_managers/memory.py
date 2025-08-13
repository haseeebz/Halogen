

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
		string = "[MEMORY]\n"
		string += "Previous chat history. A list of previous conversations between you, user and sapphire."

		return string + "\n".join(self.storage)
