import functools

#these decorators are defined here to prevent circular dependancy issues.
#moreover these are just 'markers' for their respective purposes

def SapphireCommand(name: str, info: str):
	
	def decorator(func):
		
		def wrapper(*args, **kwargs):
			return func(*args, **kwargs)
		
		wrapper._is_command = True
		wrapper._name = name
		wrapper._info = info
		
		return wrapper
	
	return decorator


def SapphireTask(name: str, info: str, args: list[str]):

	def decorator(func):
		
		def wrapper(*func_args, **kwargs):
			return func(*func_args, **kwargs)
		
		wrapper._is_task = True
		wrapper._name = name
		wrapper._info = info
		wrapper._args = args
		
		return wrapper
	
	return decorator

