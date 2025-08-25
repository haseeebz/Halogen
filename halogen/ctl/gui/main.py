import sys
from .app.window import HalogenWindow
from PySide6.QtWidgets import QApplication

def main():
	app = QApplication(sys.argv)
	win = HalogenWindow()
	win.show()
	app.exec()


if __name__ == "__main__":
	main()