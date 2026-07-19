#:=---- Imports ----=:#
from logging import Logger
from pathlib import Path
from typing import Optional

#:=-- PyQt6 --=:#
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
	QApplication,
	QMainWindow, QVBoxLayout, QStackedLayout,
	QWidget, QLabel
)

#:=-- Local --=:#
from src.portal_pyemulator.ui.screens.main_screen import MainScreen
from src.portal_pyemulator.ui.screens.portal_screen import PortalScreen
from src.portal_pyemulator.ui.screens.figure_select_screen import FigureSelectScreen


#:=---- Window Class ----=:#
class MainWindow(QMainWindow):
	def __init__(self, logger: Logger, window_size: tuple[int, int], font_dir: Path) -> None:
		super().__init__()

		self.logger = logger
		self.logger.info("Setting up MainWindow...")

		#:=---- Window Settings ----=:#
		self.setFixedSize(QSize(*window_size))
		self.setWindowTitle("Portal PyEmulator")

		#:=---- Get Fonts & Style Sheet ----=:#
		main_font_id = QFontDatabase.addApplicationFont(str(font_dir / "instrument_sans.ttf"))
		if main_font_id != -1:
			main_font = QFontDatabase.applicationFontFamilies(main_font_id)[0]
			QApplication.setFont(QFont(main_font))
			self.setStyleSheet(f"""
				* {{
					font-family: "{main_font}";
				}}
			""")
		else:
			self.logger.warning("Failed to load Instrument Sans font")

		#:=---- Build Window & Show ----=:#
		self._build()
		self._build_stack()

		self.show()

	#:=---- Private Helpers ----=:#

	def _build(self) -> None:
		self.central_widget = QWidget()
		self.layout = QVBoxLayout()

		#:=---- Stacked Layout ----=:#
		self.stack_container = QWidget()
		self.stacked_layout = QStackedLayout()

		self.stack_container.setLayout(self.stacked_layout)
		self.layout.addWidget(self.stack_container, stretch=1)

		#:=---- Footer ----=:#
		self.copyright_notice = QLabel("Copyright © 2026 Discombobulatory Studios.")
		self.copyright_notice.setStyleSheet("font-size: 12px; font-style: italic;")

		self.layout.addWidget(self.copyright_notice,
							  alignment=Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignBottom)

		#:=---- Finalisation ----=:#
		self.central_widget.setLayout(self.layout)
		self.setCentralWidget(self.central_widget)

	def _build_stack(self) -> None:
		self.logger.debug("Building Main Window stack...")

		self.screens = {
			"main":   MainScreen(self.logger),
			"portal": PortalScreen(self.logger),
			"select": FigureSelectScreen(self.logger)
		}

		for screen in self.screens.values():
			self.stacked_layout.addWidget(screen)

		self.stacked_layout.setCurrentWidget(self.screens["main"])

	#:=---- Public Helpers ----=:#

	def change_screen(self, new_screen: str) -> None:
		if new_screen not in self.screens:
			self.logger.warning(f"{new_screen} is not a valid screen; voiding change_screen.")
			return

		self.logger.info(f"Changed screen to {new_screen}.")
		self.stacked_layout.setCurrentWidget(self.screens[new_screen])