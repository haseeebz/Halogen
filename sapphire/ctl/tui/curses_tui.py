import curses, time, shlex
from sapphire.ctl.base import SapphireInterface
from sapphire.base import SapphireEvents


class SapphireTUI():

	def __init__(self, scr: curses.window):

		self.is_running = True
		self.interface = SapphireInterface("sapphire.ctl/tui")
		
		self.scr: curses.window = scr

		curses.noecho()
		curses.curs_set(0)
		self.scr.keypad(True)
		self.scr.nodelay(True)
		self.init_colors()
	
		self.height, self.width = self.scr.getmaxyx()

		self.init_event_window()
		self.init_input_window()


	def init_colors(self):
		curses.start_color()
		curses.use_default_colors()

		curses.init_pair(1, curses.COLOR_WHITE, -1)
		curses.init_pair(2, curses.COLOR_WHITE, -1)

	
	def init_event_window(self):
		self.events_win = self.scr.subwin(
			self.height - 4,
			self.width - 3,
			1,
			2
		)

		self.events_win.bkgd(" ", curses.color_pair(1))
		self.events_win.box()

		self.events_win.keypad(True)
		self.event_buffer: list[str] = []
		self.max_event_buffer_h, self.max_event_buffer_w = self.events_win.getmaxyx()
		self.max_event_buffer_h -= 2



	def init_input_window(self):

		self.input_win = self.scr.subwin(
			3,
			self.width - 3,
			self.height - 3,
			2
		)

		self.input_win.bkgd(" ", curses.color_pair(2))
		self.input_win.box()
		self.input_win.keypad(True)

		self.input_buffer: list[str] = []
		_, self.max_input_buffer = self.input_win.getmaxyx()
		self.max_input_buffer -= 4


	def handle_input_key(self, key):
		if key == curses.ERR:
			return
		
		if key == curses.KEY_BACKSPACE:
			if len(self.input_buffer) > 0: self.input_buffer.pop()
		elif key in (10, curses.KEY_ENTER): 
			input_str = "".join(self.input_buffer)
			self.parse_input(input_str)
			self.input_buffer.clear()
		else:			
			self.input_buffer.append(chr(key))

		self.show_input_buffer()

	
	def show_input_buffer(self):

		self.input_win.addstr(1, 2, " "*self.max_input_buffer)
		length = len(self.input_buffer)

		if length < self.max_input_buffer:
			displayed_buffer = self.input_buffer
		else:
			displayed_buffer = self.input_buffer[length-self.max_input_buffer:]

		self.input_win.addstr(1, 2, "".join(displayed_buffer))
		

	def show_events_buffer(self):
		y = 1
		for ev in self.event_buffer:
			self.events_win.addstr(y, 1 ,ev)
			y +=  1


	def parse_input(self, s: str):
		for s_part in s.split(";"):
			if s_part.startswith("/"):
				self.parse_command(s_part)
			else:
				self.send_user_msg(s_part)
		

	def parse_command(self, s: str):
		cmd, *args = shlex.split(s)
		cmd_parts = cmd.removeprefix("/").split("::")
		namespace = cmd_parts[0]
		name = cmd_parts[1]

		self.interface.send_command(namespace, name, args)


	def send_user_msg(self, s: str):
		self.interface.send_message(s)
		self.event_buffer.append(f"You: {s}")
		self.show_events_buffer()


	def run(self):

		self.interface.start()

		while self.is_running:
			key = self.scr.getch()
			self.handle_input_key(key)

			self.input_win.refresh()
			self.events_win.refresh()
			time.sleep(0.01)

		self.interface.end()


def main(scr):
	tui = SapphireTUI(scr)
	tui.run()

curses.wrapper(main)