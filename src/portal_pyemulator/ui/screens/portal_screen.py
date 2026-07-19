 #:=---- Imports ----=:#
from logging import Logger

#:=-- Local --=:#
from src.portal_pyemulator.ui.widgets.emulated_slot_widget import EmulatedSlotWidget
from src.portal_pyemulator.ui.widgets.physical_slot_widget import PhysicalSlotWidget

#:=-- PySide6 --=:#
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
	QVBoxLayout,
	QWidget, QLabel, QScrollArea
)


#:=---- Portal Screen ----=:#
class PortalScreen(QWidget):
	def __init__(self, logger: Logger) -> None:
		super().__init__()

		self.logger = logger
		self.logger.info("Setting up MainScreen...")

		#:=-- Build Screen --=:#
		self._build()

	def _build(self) -> None:
		self.central_layout = QVBoxLayout()

		#:=---- Header ----=:#
		#:=-- Title --=:#
		self.title_label = QLabel("Portal PyEmulator")
		self.central_layout.addWidget(self.title_label)

		#:=---- Scroll Area ----=:#
		self.scroll = QScrollArea()
		self.scroll_layout = QVBoxLayout()

		#:=-- ScrollArea Setup --=:#
		self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.scroll.setWidgetResizable(True)

		#:=-- Slots --=:#
		self.slots = []
		for i in range(1, 9):
			slot = EmulatedSlotWidget(i)
			self.slots.append(slot)
			self.scroll_layout.addWidget(slot, alignment=Qt.AlignmentFlag.AlignHCenter)

		for i in range(9, 19):
			phys_slot = PhysicalSlotWidget(i)
			self.slots.append(phys_slot)
			self.scroll_layout.addWidget(phys_slot, alignment=Qt.AlignmentFlag.AlignHCenter)

		#:=---- Finalization ----=:#
		self.scroll.setLayout(self.scroll_layout)
		self.central_layout.addWidget(self.scroll)
		self.setLayout(self.central_layout)