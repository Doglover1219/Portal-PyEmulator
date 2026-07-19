#:=---- Imports ----=:#
from logging import Logger

#:=-- Local --=:#
from src.portal_pyemulator.portal_emulation.slot import Slot


#:=---- Slots Handler ----=:#
class SlotsHandler:
	def __init__(self, logger: Logger) -> None:
		self.logger = logger
		self.logger.info("Setting up SlotsHandler...")