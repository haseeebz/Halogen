import functools

#these decorators are defined here to prevent circular dependancy issues.
#moreover these are just 'markers' for their respective purposes

def HalogenCommand(name: str, info: str):
	
	def decorator(func):
		
		def wrapper(*args, **kwargs):
			return func(*args, **kwargs)
		
		wrapper._is_command = True
		wrapper._name = name
		wrapper._info = info
		
		return wrapper
	
	return decorator

