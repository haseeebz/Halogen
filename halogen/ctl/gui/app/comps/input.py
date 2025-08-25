from PySide6.QtWidgets import (
	QWidget,
	QHBoxLayout,
	QLineEdit
)
from PySide6.QtCore import Qt, Signal
from halogen.modules.server import HalogenInterface


class InputBar(QLineEdit):
	message_submitted = Signal(str)

	def __init__(self):
		super().__init__()
		self.setObjectName("input-bar")
		self.returnPressed.connect(self._on_return)

	def _on_return(self):
		text = self.text().strip()
		self.clear()
		if text:
			self.message_submitted.emit(text)
