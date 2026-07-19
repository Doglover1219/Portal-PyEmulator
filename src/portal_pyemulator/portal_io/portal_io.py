#:=---- Imports ----=:#
import usb.core
import usb.util
import usb.backend.libusb1

from logging import Logger
from pathlib import Path
from queue import Queue
from typing import Optional

#:=-- Local --=:#
from portal_pyemulator.portal_io.command_handler   import CommandHandler
from src.portal_pyemulator.portal_io.read_handler  import ReadHandler
from src.portal_pyemulator.portal_io.music_handler import MusicHandler


#:=---- Portal IO ----=:#
class PortalIO:
	def __init__(self, main_logger: Logger, stream_logger: Logger, portal_vid: int, portal_pid: int, dll_path: Path) -> None:
		"""Handle the Portal IO.

		Args:
			main_logger (Logger): The main logger.
			stream_logger (Logger): The stream logger.
			portal_vid (int): The Portal of Power's Vendor ID.
			portal_pid (int): The Portal of Power's Product ID.
		"""
		self.logger = main_logger
		self.logger.info("Setting up PortalIO...")

		self.stream_logger = stream_logger

		#:=---- Test the Backend ----=:#
		backend = usb.backend.libusb1.get_backend(
			find_library=lambda x: str(dll_path)
		)
		if backend is None:
			self.logger.warning(f"No USB Backend Found; Voiding PortalIO... ({backend=})")
			return

		#:=---- Get the Portal ----=:#
		self.portal_vid = portal_vid
		self.portal_pid = portal_pid

		portal = self._get_portal(portal_vid, portal_pid)
		if portal is None:
			self.logger.warning("Portal of Power not connected; Voiding PortalIO...")
			return

		device: usb.core.Device = portal[0]
		endpoint_in: usb.core.Endpoint = portal[1]
		endpoint_out: usb.core.Endpoint = portal[2]

		#:=---- Setup the Handlers ----=:#
		self.input_queues: dict[str, Queue[bytes]] = {}

		self.control_handler = CommandHandler(self.logger, device, self.input_queues)
		self.read_handler    = ReadHandler(self.logger, self.stream_logger, endpoint_in, self.input_queues)
		self.music_handler   = MusicHandler(self.logger, endpoint_out)

	def is_ok(self) -> bool:
		test_ok = True
		if getattr(self, "portal_pid", None) is None:
			test_ok = False
		if getattr(self, "control_handler", None) is None:
			test_ok = False
		return test_ok

	@staticmethod
	def _get_portal(vid: int, pid: int) -> Optional[tuple[usb.core.Device, usb.core.Endpoint, usb.core.Endpoint]]:
		"""Get the Portal of Power USB Device.

		Args:
			vid (int): The Portal of Power's Vendor ID.
			pid (int): The Portal of Power's Product ID.

		Returns:
			Optional[tuple[Device, Endpoint, Endpoint]]: The Portal of Power USB Device and its Endpoints IN and OUT.
		"""
		device: Optional[usb.core.Device] = usb.core.find(idVendor=vid, idProduct=pid)
		if not isinstance(device, usb.core.Device):
			return None

		device.set_configuration()

		cfg = device.get_active_configuration()
		intf = cfg[(0, 0)]

		ep_out = usb.util.find_descriptor(intf, custom_match=
				lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)

		ep_in = usb.util.find_descriptor(intf, custom_match=
				lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)

		return device, ep_in, ep_out