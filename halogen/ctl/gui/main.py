import sys
from .app.window import Window
from PySide6.QtWidgets import QApplication

def main():
	app = QApplication(sys.argv)
	win = Window()
	win.show()
	app.exec()


if __name__ == "__main__":
	main()