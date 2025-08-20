from halogen.base import HalogenEvents


task_intro = """
[TASKS]
All available tasks that you can do. These namespaces are modules and their defined tasks are given below. 
These are the functions that you can execute.
Make sure to follow the argument types indicated after the ':' and in python type hint format.

"""


class TasksManager():

	def __init__(self):
		self.task_map: dict[str, list[tuple[str, str, list[str]]]] = {}
		self.task_string = ""

	def add_task(self, ev: HalogenEvents.TaskRegisteredEvent):
		task_list = self.task_map.setdefault(ev.namespace, [])
		data = (ev.task_name, ev.info, ev.args_info)
		task_list.append(data)
		self.make_task_section()

	def make_task_section(self):

		string = []
		string.append(task_intro)

		for ns, taskslist in self.task_map.items():
			string.append(f"\n> Namespace: '{ns}'\nDefined Tasks:")
			for n, i, a in taskslist:
				string.append(f"- name: '{n}'; args: ({a}); info: {i};")
			
		self.tasks_section_string = "\n".join(string)

	def stringify(self) -> str:
		return self.tasks_section_string