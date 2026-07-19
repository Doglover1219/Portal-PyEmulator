#:=---- Imports ----=:#
from logging import Logger

#:=-- PyQt6 --=:#
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
	QVBoxLayout,
	QWidget, QLabel, QPushButton
)


#:=---- Main Screen ----=:#
class MainScreen(QWidget):
	buttonStartEmulatorClicked = Signal()
	buttonControlPortalClicked = Signal()

	def __init__(self, logger: Logger) -> None:
		super().__init__()

		self.logger = logger
		self.logger.info("Setting up MainScreen...")

		#:=---- Build Screen ----=:#
		self._build()

	def _build(self) -> None:
		self.central_layout = QVBoxLayout()

		#:=---- Header ----=:#
		#:=-- Title --=:#
		self.title_label = QLabel("Portal PyEmulator")
		self.title_label.setStyleSheet("font-size: 48px; font-weight: 800;")

		self.central_layout.addWidget(self.title_label,
				alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

		#:=-- Subtitle --=:#
		self.subtitle_label = QLabel("Discombobulatory Studios")
		self.subtitle_label.setStyleSheet("font-size: 24px; font-style: italic; font-weight: 400;")

		self.central_layout.addWidget(self.subtitle_label,
				alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

		#:=---- Main Layout ----=:#
		self.main_widget = QWidget()
		self.main_layout = QVBoxLayout()

		self.button_start_emulator = QPushButton("Start the Emulator")
		self.button_start_emulator.clicked.connect(self.buttonStartEmulatorClicked)
		self.main_layout.addWidget(self.button_start_emulator,
				alignment=Qt.AlignmentFlag.AlignHCenter)

		self.button_control_portal = QPushButton("Control the Portal")
		self.button_control_portal.clicked.connect(self.buttonControlPortalClicked)
		self.main_layout.addWidget(self.button_control_portal,
				alignment=Qt.AlignmentFlag.AlignHCenter)

		#:=---- Finalization ----=:#
		self.main_widget.setLayout(self.main_layout)
		self.central_layout.addWidget(self.main_widget, stretch=1,
				alignment=Qt.AlignmentFlag.AlignCenter)

		self.setLayout(self.central_layout)