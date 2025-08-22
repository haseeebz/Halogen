from PySide6.QtWidgets import (
	QWidget,
	QVBoxLayout,
	QScrollArea
)
from PySide6.QtCore import QThread

from halogen.modules.server import HalogenInterface

class ViewBoard(QWidget):

	def __init__(self, interface: HalogenInterface):
		self.interface = interface
		self.view = QScrollArea()