#:=---- Imports ----=:#
#:=-- Local --=:#
from src.portal_pyemulator.ui.widgets.slot_widget import SlotWidget


#:=---- Physical Slot Widget ----=:#
class PhysicalSlotWidget(SlotWidget):
	def __init__(self, slot: int) -> None:
		super().__init__(slot)

		#:=-- Finish Building Widget --=:#
		self._post_build()

	def _post_build(self) -> None:
		...