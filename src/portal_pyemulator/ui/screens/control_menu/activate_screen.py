#:=---- Imports ----=:#
from logging import Logger

#:=-- PySide6 --=:#
from PySide6.QtWidgets import (
	QVBoxLayout,
	QWidget
)


#:=---- Activate Screen ----=:#
class ActivateScreen(QWidget):
	def __init__(self, logger: Logger) -> None:
		super().__init__()

		self.logger = logger
		self.logger.info("Setting up Activate Screen...")

		self._build()

	def _build(self) -> None:
		self.central_layout = QVBoxLayout()