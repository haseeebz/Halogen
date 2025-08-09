from dataclasses import dataclass

@dataclass(frozen = True)
class Chain():
	"""
	An event's identifier giving insight on:
	1) What caused the event (via flow)
	2) Where the root event orignally started from (via context)

	Context is the absolute origin of an event. Context 0 is used for sapphire itself while
	all contexts after that are reserved for clients.
	This same context id is used by Sapphire Server to route response events to clients that
	sent it.

	Flow is the actual 'chain of events'. Events with the same flow (and obviously context) are in
	the same chain.
	"""

	context: int
	flow: int

	def __str__(self) -> str:
		return f"({self.context}:{self.flow})"
	
	def __repr__(self) -> str:
		return self.__str__()
	
	def __eq__(self, other) -> bool:
		return (self.context, self.flow) == (other.context, other.flow)
	