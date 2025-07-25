import functools

def SapphireCommand(name: str, info: str):
	
	def decorator(func):
		
		def wrapper(*args, **kwargs):
			return func(*args, **kwargs)
		
		wrapper._is_command = True
		wrapper._name = name
		wrapper._info = info
		
		return wrapper
	
	return decorator