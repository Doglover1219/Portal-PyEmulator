#:=---- Imports ----=:#
from typing import Literal

#:=-- PySide6 --=:#
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
	QStackedLayout, QHBoxLayout, QVBoxLayout,
	QWidget, QPushButton
)


#:=---- Vertical Tab Widget ----=:#
class VerticalTabWidget(QWidget):
	changeTab = Signal(str)

	def __init__(self, buttons_side: Literal["left", "right"]) -> None:
		super().__init__()

		self._tabs: dict[str, tuple[QPushButton, QWidget]] = {}

		self.changeTab.connect(self.change_tab)

		self.central_layout = QHBoxLayout()

		#:=---- Button Side ----=:#
		self.button_widget = QWidget()
		self.button_layout = QVBoxLayout()

		self.button_widget.setLayout(self.button_layout)

		#:=---- Stack Side ----=:#
		self.stack_widget = QWidget()
		self.stack_layout = QStackedLayout()

		#:=---- Finalization ----=:#
		self.stack_widget.setLayout(self.stack_layout)

		if buttons_side == "left":
			self.central_layout.addWidget(self.button_widget)
			self.central_layout.addWidget(self.stack_widget)
		else:
			self.central_layout.addWidget(self.stack_widget)
			self.central_layout.addWidget(self.button_widget)

		self.setLayout(self.central_layout)

	def add_tab(self, title: str, widget: QWidget) -> None:
		if title in self._tabs.keys():
			raise ValueError(f"Tab {title} already added to widget!")

		button = QPushButton(title)
		button.clicked.connect(lambda *_: self.changeTab.emit(title))
		self.button_layout.addWidget(button)

		self._tabs[title] = (button, widget)
		self.stack_layout.addWidget(widget)

	def change_tab(self, tab_title: str) -> None:
		if tab_title not in self._tabs:
			return
		self.stack_layout.setCurrentWidget(self._tabs[tab_title][1])