from PySide6.QtWidgets import (
	QWidget,
	QVBoxLayout,
	QScrollArea,
	QLineEdit
)
from pathlib import Path
from halogen.modules.server import HalogenInterface

class Window(QWidget):
	
	def __init__(self):
		super().__init__()
		self.setObjectName("window")
		self.set_style_sheet()
		self.interface = HalogenInterface("Halogen-GUI")

	def set_style_sheet(self):
		with open(Path(__file__).resolve().parent/"style.qss") as file:
			stylesheet = file.read()
		self.setStyleSheet(stylesheet)
