from PySide6.QtWidgets import (
	QWidget,
	QScrollArea,
	QVBoxLayout,
	QHBoxLayout,
	QLabel,
	QFrame
)
from halogen.modules.server import HalogenInterface
from halogen.base import HalogenEvents


class MessageBox(QFrame):

	def __init__(self, text: str):
		super().__init__()
		self.setObjectName("message-box")
		self.setFrameShape(QFrame.StyledPanel)
		
		layout = QHBoxLayout(self)
		self.label = QLabel(text)
		self.label.setWordWrap(True)
		layout.addWidget(self.label)


class EventBoard(QScrollArea):

	def __init__(self):
		super().__init__(None)
		self.setWidgetResizable(True)

		self.container = QWidget()
		self.layout = QVBoxLayout(self.container)
		self.layout.addStretch()  

		self.setWidget(self.container)

	def add_event(self, ev: HalogenEvents.Event):

		if not isinstance(ev, (HalogenEvents.AIResponseEvent, HalogenEvents.UserInputEvent)):
			return
		msg = MessageBox(ev.message)
		self.layout.insertWidget(self.layout.count() - 1, msg)  
		self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())  
