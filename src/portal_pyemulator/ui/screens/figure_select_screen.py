#:=---- Imports ----=:#
from logging import Logger

#:=---- PySide6 ----=:#
from PySide6.QtWidgets import QWidget


#:=---- Figure Select Screen ----=:#
class FigureSelectScreen(QWidget):
	def __init__(self, logger: Logger) -> None:
		super().__init__()

		self.logger = logger
		self.logger.info("Setting up FigureSelectScreen...")

		#:=-- Build Screen --=:#
		self._build()

	def _build(self) -> None:
		...