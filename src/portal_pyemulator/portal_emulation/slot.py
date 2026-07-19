#:=---- Imports ----=:#
from dataclasses import dataclass, field
from typing import Optional


#:=---- Slot Dataclass ----=:#
@dataclass
class Slot:
	#:=-- Init Fields --=:#
	...

	#:=-- Non-Init Fields --=:#
	is_active: bool = field(default=False, init=False)
	maps_to_slot: Optional[int] = field(default=None, init=False)

	last_figure: Optional[tuple[int, int]] = field(default_factory=tuple, init=False)
