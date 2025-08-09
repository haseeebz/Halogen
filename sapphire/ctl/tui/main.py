from sapphire.ctl.base import SapphireInterface
from sapphire.base import SapphireEvents

import curses, time, threading, shlex

# TODO 
# maybe abstract the curses gui part into a seperate class?
# make the event screen


class SapphireCtl():

	def __init__(self):
		self.lock = threading.Lock()
		self.interface = SapphireInterface("sapphire-ctl/tui")
		self.is_running = True

	def init(self, scr: curses.window):

		self.scr: curses.window = scr

		curses.noecho()
		curses.curs_set(0)

		self.scr.keypad(True)
		self.scr.nodelay(True)

		curses.start_color()
		curses.use_default_colors()


		curses.init_pair(1, curses.COLOR_WHITE, -1)
		curses.init_pair(2, curses.COLOR_WHITE, -1)

		
		self.height, self.width = self.scr.getmaxyx()

		self.init_main_window()
		self.init_input_window()
		self.run()


	def init_main_window(self):
		
		self.window = curses.newwin(
			self.height - 1,
			self.width - 2,
			1,
			2
		)

		self.window.bkgd(" ", curses.color_pair(1))
		self.window.box()

		self.window.keypad(True)
		self.window_event_buffer: list[str] = []
		self.max_event_buffer_h, self.max_event_buffer_w = self.window.getmaxyx()
		self.max_event_buffer_h -= 2


	def init_input_window(self):
		h, w = self.window.getmaxyx()


		self.input_window = self.window.subwin(
			3,
			w - 4,
			h - 3,
			4
		)

		self.input_window.bkgd(" ", curses.color_pair(2))
		self.input_window.box()
		self.input_window.keypad(True)

		self.input_buffer: list[str] = []
		_, self.max_input_buffer = self.input_window.getmaxyx()
		self.max_input_buffer -= 4

	
	def run(self):

		self.interface.start()
		while self.is_running:
			key = self.scr.getch()
			self.handle_key(key)

			event = self.interface.check_event(0.05)
			if event:
				self.handle_event(event)

			self.input_window.refresh()
			self.window.refresh()
			time.sleep(0.01)

		self.interface.end()


	def handle_key(self, key):
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

		self.input_window.addstr(1, 1, " "*self.max_input_buffer)
		length = len(self.input_buffer)

		if length < self.max_input_buffer:
			displayed_buffer = self.input_buffer
		else:
			displayed_buffer = self.input_buffer[length-self.max_input_buffer:]

		self.input_window.addstr(1, 1, "".join(displayed_buffer))
		

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
		self.window_event_buffer.append(f"You: {s}")
		self.show_events_buffer()

	def handle_event(self, ev: SapphireEvents.Event):
		match ev:
			case SapphireEvents.AIResponseEvent():
				self.window_event_buffer.append(f"AI: {ev.message}")
				self.show_events_buffer()


	def show_events_buffer(self):
		y = 1
		for ev in self.window_event_buffer:
			self.window.addstr(y, 1 ,ev)
			y +=  1


	

def main():
	ctl = SapphireCtl()
	curses.wrapper(ctl.init)

if __name__ == "__main__":
	main()