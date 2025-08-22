from PySide6.QtWidgets import (
	QWidget,
	QHBoxLayout,
	QLineEdit
)
from halogen.modules.server import HalogenInterface

class InputBox(QWidget):

	def __init__(self, interface: HalogenInterface):
		self.interface = interface

		self.setObjectName("input-box")

		self.layout_box = QHBoxLayout()

		self.line_edit = QLineEdit()
		self.layout_box.addWidget(self.line_edit)

		self.setLayout(self.layout_box)

