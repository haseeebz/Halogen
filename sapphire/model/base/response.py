from typing import Any
from pydantic import BaseModel


class ModelTask(BaseModel):
	func: str
	args: list[str]

class ModelExtras(BaseModel):
	key: str
	value: Any

class ModelResponse(BaseModel):
	"Use this class if the model can be configured using schema directly."
	message: str
	tasks: list[ModelTask] 
	extras: list[ModelExtras]
