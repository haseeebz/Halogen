
class Color:
	RESET = "\033[0m"
	RED = "\033[31m"
	GREEN = "\033[32m"
	YELLOW = "\033[33m"
	BLUE = "\033[34m"
	MAGENTA = "\033[35m"
	CYAN = "\033[36m"
	GRAY = "\033[90m"

	@staticmethod
	def colorify(text:str, color):
		return f"{color}{text}{Color.RESET}"
	