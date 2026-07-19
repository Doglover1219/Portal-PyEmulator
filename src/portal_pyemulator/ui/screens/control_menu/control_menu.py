#:=---- Imports ----=:#
from logging import Logger

#:=-- PySide6 --=:#
from PySide6.QtWidgets import (
	QHBoxLayout,
	QWidget, QTextEdit
)


#:=---- Control Menu ----=:#
class ControlMenu(QWidget):
	def __init__(self, logger: Logger) -> None:
		super().__init__()

		self.logger: Logger = logger
		self.logger.info("Setting up Control Menu...")

	def _build(self) -> None:
		...