#:=---- Imports ----=:#
import sys

#:=-- Local --=:#
import src.portal_pyemulator.helpers as helpers

from src.portal_pyemulator.portal_pyemulator import PortalPyEmulator


#:=---- Setup & Execute ----=:#
def main() -> None:
	main_logger, stream_logger = helpers.get_loggers()

	portal_emulator = PortalPyEmulator(main_logger, stream_logger)

	sys.exit(portal_emulator.exec())

if __name__ == "__main__":
	main()