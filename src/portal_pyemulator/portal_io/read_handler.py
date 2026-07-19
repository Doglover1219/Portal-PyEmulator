#:=---- Imports ----=:#
import usb.core

from logging import Logger
from queue import Queue
from threading import Thread, Event
from typing import Optional

#:=-- Local --=:#
import src.portal_pyemulator.helpers as helpers


#:=---- Read Handler ----=:#
class ReadHandler:
	def __init__(
			self,
			main_logger: Logger,
			stream_logger: Logger,
			endpoint_in: usb.core.Endpoint,
			input_queues: dict[str, Queue[bytes]]
		) -> None:
		"""A handler to continuously read the Portal's incoming messages.

		Args:
			main_logger (Logger): Main logger.
			stream_logger (Logger): Logger for the USB input stream.
			endpoint_in (usb.core.Endpoint): USB endpoint IN.
			input_queues (dict[str, Queue]): Dictionary of input queues.
		"""
		self.logger = main_logger
		self.logger.info("Setting up InputHandler...")

		self.stream_logger = stream_logger
		self.endpoint_in = endpoint_in
		self.input_queues = input_queues

		self.running = Event()
		self.thread: Optional[Thread] = None

	def _read_loop(self) -> None:
		"""Continuously read the Portal of Power output stream."""
		stream_logger = self.stream_logger
		endpoint_in = self.endpoint_in
		input_queues = self.input_queues

		while self.running.is_set():
			try:
				packet = endpoint_in.read(64, timeout=1_000)
			except usb.core.USBTimeoutError:
				continue
			except usb.core.USBError as e:
				self.logger.debug(f"USB Exception occurred during read loop: {e}")
				raise
			except Exception as e:
				self.logger.debug(f"Unknown exception occurred during read loop: {e}")
				raise

			cmd_type, log_packet = helpers.bytes_to_str(packet)
			stream_logger.info(log_packet)

			queue = input_queues.setdefault(cmd_type, Queue())
			queue.put(packet)

	def init_read_loop(self) -> None:
		"""Initialize the read loop on a thread."""
		self.logger.info("Initialising read loop...")

		self.running.set()
		self.thread = Thread(target=self._read_loop)
		self.thread.start()  # type: ignore

	def stop_read_loop(self) -> None:
		"""Stop the read loop."""
		self.running.clear()

		if self.thread:
			self.thread.join()