from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLineEdit

from PySide6.QtCore import Qt, Signal
from threading import Thread

from pathlib import Path
from halogen.modules.server import HalogenInterface
from halogen.base import HalogenEvents

from .comps.eventboard import EventBoard
from .comps.input import InputBar


class HalogenWindow(QWidget):
	event_received = Signal(HalogenEvents.Event)

	def __init__(self):
		super().__init__()
		self.setObjectName("halogen-window")
		self.setWindowTitle("Halogen")
		self.interface = HalogenInterface("Halogen-GUI")
		self.resize(700, 600)
		self.set_style_sheet()
		self.initUI()
		self.interface.start()
		self.event_thread = Thread(target = self.EventRead)
		self.event_thread.start()
		


	def set_style_sheet(self):
		with open(Path(__file__).resolve().parent/"style.qss") as file:
			stylesheet = file.read()
		self.setStyleSheet(stylesheet)


	def initUI(self):
		self.event_board = EventBoard()
		self.input_box = InputBar()

		layout = QVBoxLayout(self)
		layout.addWidget(self.event_board)
		layout.addWidget(self.input_box)

		self.input_box.message_submitted.connect(self.send_input)
		self.event_received.connect(self.event_board.add_event)

	def EventRead(self):

		while True:
			ev = self.interface.check_event(0.1)

			if ev: self.event_received.emit(ev)


	def send_input(self, text: str):
		self.interface.send_message(text)
