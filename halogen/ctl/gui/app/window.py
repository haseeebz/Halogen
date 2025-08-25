from PySide6.QtWidgets import (
	QWidget,
	QVBoxLayout,
	QScrollArea,
	QLineEdit
)
from pathlib import Path
from halogen.modules.server import HalogenInterface
from .comps.chatarea import ChatArea
from .comps.input import InputBar


class HalogenWindow(QWidget):
	
	def __init__(self):
		super().__init__()
		self.setObjectName("halogen-window")
		self.interface = HalogenInterface("Halogen-GUI")
		self.resize(700, 600)
		self.set_style_sheet()
		self.initUI()


	def set_style_sheet(self):
		with open(Path(__file__).resolve().parent/"style.qss") as file:
			stylesheet = file.read()
		self.setStyleSheet(stylesheet)


	def initUI(self):
		self.chat_area = ChatArea()
		self.input_box = InputBar()

		layout = QVBoxLayout(self)
		layout.addWidget(self.chat_area)
		layout.addWidget(self.input_box)

		self.input_box.message_submitted.connect(lambda a: print(a))



