#:=---- Imports ----=:#
#:=-- PySide6 --=:#
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
	QHBoxLayout,
	QWidget, QLabel
)


#:=---- Slot Widget ----=:#
class SlotWidget(QWidget):
	def __init__(self, slot: int) -> None:
		super().__init__()

		self.slot = slot

		#:=-- Setup Widget --=:#
		self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
		self.setFixedSize(500, 60)
		self.setProperty("class", "SlotWidget")
		self.setStyleSheet("""
			QWidget[class="SlotWidget"] {
				background-color: #919191;
				border: 3px solid black;
				border-radius: 5px;
			}

			QLabel {
				color: black;
				font-size: 20px;
				border: 2px solid black; 
				border-radius: 5px;
			}
		""")

		#:=-- Build Widget --=:#
		self._build()

	def _build(self) -> None:
		self.main_layout = QHBoxLayout()
		self.main_layout.setContentsMargins(5, 5, 5, 5)

		self.slot_label = QLabel(f"{self.slot}.")
		self.slot_label.setFixedWidth(15)
		self.slot_label.setStyleSheet("font-size: 14px; border: 0px solid black;")
		self.main_layout.addWidget(self.slot_label, 1)

		self.name_label = QLabel("No Figure Selected")
		self.name_label.setStyleSheet("font-size: 16px;")
		self.main_layout.addWidget(self.name_label, 2)

		self.setLayout(self.main_layout)

	def on_figure_selected(self, figure_name: str|None) -> None:
		if figure_name is not None:
			self.name_label.setText(figure_name)
		else:
			self.name_label.setText("No Figure Selected")