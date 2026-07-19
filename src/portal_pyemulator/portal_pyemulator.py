#:=---- Imports ----=:#
import sys

from logging import Logger
from PySide6.QtWidgets import QApplication

#:=-- Local --=:#
import src.portal_pyemulator.helpers as helpers

from src.portal_pyemulator.storage.data_exporter import DataExporter
from src.portal_pyemulator.portal_io.portal_io import PortalIO
from src.portal_pyemulator.ui.window import MainWindow


#:=---- Portal PyEmulator Class ----=:#
class PortalPyEmulator:
	def __init__(self, main_logger: Logger, stream_logger: Logger) -> None:
		self.logger = main_logger
		self.logger.info("Setting up PortalPyEmulator...")

		self.stream_logger = stream_logger

		#:=---- Storage ----=:#
		self.data_exporter = DataExporter(self.logger)

		#:=---- Portal of Power ----=:#
		self.portal_vid = 0x1430
		self.portal_pid = 0x0150

		#:=---- UI ----=:#
		font_dir = helpers.get_asset_path("fonts/")

		self.qt_app = QApplication(sys.argv)
		self.window = MainWindow(self.logger, (1000, 625), font_dir)

		self.window.screens["main"].buttonStartEmulatorClicked.connect(self._on_start_emulator)
		self.window.screens["main"].buttonControlPortalClicked.connect(self._on_start_portal)

	def _get_portal(self) -> None:
		dll_path = helpers.get_asset_path("dll/libusb-1.0.dll")

		if not dll_path.is_file():
			self.logger.error(f"assets/dll/libusb-1.0.dll not found. ({dll_path=}")

		self.portal_io = PortalIO(self.logger, self.stream_logger, self.portal_vid, self.portal_pid, dll_path=dll_path)
		self.portal_ok = self.portal_io.is_ok()

	def _on_start_portal(self) -> None:
		self._get_portal()

		...

	def _on_start_emulator(self) -> None:
		self._get_portal()
		...

	def exec(self) -> int:
		self.logger.info("Executing PortalPyEmulator...")

		exit_code = self.qt_app.exec()

		# Shutdown logic

		return exit_code