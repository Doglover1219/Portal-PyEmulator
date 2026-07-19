#:=---- Imports ----=:#
#:=-- PySide6 --=:#
from PySide6.QtCore import Signal, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
	QPushButton
)

#:=-- Local --=:#
import src.portal_pyemulator.helpers as helpers

from src.portal_pyemulator.ui.widgets.slot_widget import SlotWidget


#:=---- Slot Widget ----=:#
class EmulatedSlotWidget(SlotWidget):
	figure_remove = Signal()
	figure_reset = Signal()

	def __init__(self, slot: int) -> None:
		super().__init__(slot)

		self.setStyleSheet(self.styleSheet() + """
			QPushButton {
				background-color: #FFFFFF;
				border: 2px solid black;
				border-radius: 5px;
			}

			QPushButton:hover {
				background-color: #AAAAAA;
			}

			QPushButton:pressed {
				background-color: #888888;
			}
		""")

		#:=-- Finish Building Widget --=:#
		self._post_build()

	def _post_build(self) -> None:
		button_size = (50, 50)

		#:=-- Remove Button --=:#
		self.remove_button = QPushButton()
		self.remove_button.setFixedSize(*button_size)

		self.remove_button.setIcon(QIcon(str(helpers.get_asset_path("textures/remove.png"))))
		self.remove_button.setIconSize(QSize(*button_size))

		self.remove_button.clicked.connect(self.figure_remove.emit)
		self.main_layout.addWidget(self.remove_button)

		#:=-- Reset Button --=:#
		self.reset_button = QPushButton()
		self.reset_button.setFixedSize(*button_size)

		self.reset_button.setIcon(QIcon(str(helpers.get_asset_path("textures/reset.png"))))
		self.reset_button.setIconSize(QSize(*button_size))

		self.reset_button.clicked.connect(self.figure_reset.emit)
		self.main_layout.addWidget(self.reset_button)