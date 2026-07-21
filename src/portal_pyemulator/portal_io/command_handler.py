#:=---- Imports ----=:#
import queue

import usb.core

from logging import Logger
from queue import Queue
from typing import Optional, Literal, overload

#:=-- Local --=:#
import src.portal_pyemulator.helpers as helpers

from src.portal_pyemulator.portal_io.command_type import CommandType


#:=---- Command Handler ----=:#
class CommandHandler:
	def __init__(self, logger: Logger, portal: usb.core.Device, input_queues: dict[str, Queue[bytes]]) -> None:
		self.logger = logger
		self.logger.info("Setting up ControlHandler...")

		self.portal = portal
		self.input_queues = input_queues

	#:=---- Helpers ----=:#
	#:=-- Private --=:#
	@staticmethod
	def _build_command(cmd_type: CommandType, *data: bytes) -> bytearray:
		"""Build a command packet to send to the Portal of Power

		Args:
			cmd_type: The type of command to send (determines first byte).
			data: The data to send to the Portal.

		Returns:
			bytearray: The built command packet.
		"""
		packet = bytearray(32)
		packet[0] = cmd_type

		offset = 1
		for datum in data:
			packet[offset:offset + len(datum)] = datum
			offset += len(datum)

		return packet

	@staticmethod
	def _rgb_u8(r: int, g: int, b: int) -> tuple[bytes, bytes, bytes]:
		"""Verify the colour values are between 0 and 255 and raise an error if not.

		Args:
			r: The red colour value.
			g: The green colour value.
			b: The blue colour value.

		Returns:
			The rgb colour values in bytes.

		Raises:
			ValueError: If any colour values is outside the range of 0 to 255.
		"""
		return (
			helpers.uint(r, 8),
			helpers.uint(g, 8),
			helpers.uint(b, 8)
		)

	def _get_command_response(self, cmd_type, *, timeout_sec: Optional[float|int] = 10) -> Optional[bytes]:
		try:
			response = self.input_queues[cmd_type].get(timeout=timeout_sec)
			return response
		except queue.Empty:
			return None

	#:=-- Public --=:#
	def send_command(self, packet: bytes) -> None:
		"""Send a control command to the Power of Power that does not expect a response.

		Args:
			packet: The control command to send.
		"""
		self.logger.info(f"Sending Control Command: {helpers.bytes_to_str(packet)[1]}")

		self.portal.ctrl_transfer(0x21, 0x09, 0x0200, 0x00, packet)

	@overload
	def send_response_command(self, packet: bytes, *, timeout_sec: None = None, retries: int = 1) -> bytes:
		...

	@overload
	def send_response_command(self, packet: bytes, *, timeout_sec: float|int, retries: int = 1) -> Optional[bytes]:
		...

	def send_response_command(self, packet: bytes, *, timeout_sec: Optional[float|int] = 10, retries: int = 1) -> Optional[bytes]:
		"""
		Send a control command to the Portal of Power that expects a response.

		Args:
			packet: The control command to send.
			timeout_sec: If not None, after how many seconds to timeout. Defaults to 10.
			retries: How many times to retry sending the command (-1 = infinite). Defaults to 1.

		Returns:
			The response packet.
		"""
		cmd_type = chr(packet[0])
		if cmd_type not in self.input_queues:
			self.input_queues[cmd_type] = Queue()

		self.send_command(packet)

		self.logger.debug(f"Waiting for response to command... ({cmd_type=}, {timeout_sec=}, {retries=})")

		response = self._get_command_response(cmd_type, timeout_sec=timeout_sec)
		if response is not None:
			return response

		if retries < 0:
			while True:
				response = self._get_command_response(cmd_type, timeout_sec=timeout_sec)
				if response is not None:
					break

				self.send_command(packet)

			return response

		# retries >= 0
		for i in range(retries):
			self.send_command(packet)
			response = self._get_command_response(cmd_type, timeout_sec=timeout_sec)

			if response is not None:
				return response

		self.logger.debug("Response timed out.")
		return None


	#:=---- Commands ----=:#
	def activate(self, do_activate: bool) -> bytes:
		"""
		Send the Activate (A) command to the Portal of Power. (Receives response)\n
		Activates and deactivates the Portal.

		Args:
			do_activate: Whether to activate or deactivate the Portal of Power.

		Returns:
			Mirrors the command with addition of unknown constants 0xFF and 0x77.
		"""
		packet = self._build_command(
			CommandType.ACTIVATE,
			helpers.uint(do_activate, 8)
		)

		response = self.send_response_command(packet)
		return response

	def color(self, r: int, g: int, b: int) -> None:
		"""
		Send the Colour (C) command to the Portal of Power.\n
		Sets the LED colours in the Portal to a specified colour value.\n
		No response.

		Args:
			r: The red colour value.
			g: The green colour value.
			b: The blue colour value.
		"""
		colors = self._rgb_u8(r, g, b)

		packet = self._build_command(
			CommandType.COLOR,
			*colors
		)

		self.send_command(packet)

	def color_fade(self, side: Literal[0x00, 0x02, "left", "right"], r: int, g: int, b: int, fade_ms: int) -> bytes:
		"""
		Send the Colour Fade (J) command to the Portal of Power. (Receives response; Traptanium Portal only)\n
		Fade the LED colours of the chosen side in the Portal to a specified colour value.

		Args:
			side: The side to set the colour of (0x00 = left, 0x02 = right).
			r: The red colour value.
			g: The green colour value.
			b: The blue colour value.
			fade_ms: The amount of time to fade from the previous colour to this colour.

		Returns:
			The Portal's signal that the timer has started (`J`).
		"""
		colors = self._rgb_u8(r, g, b)

		if side not in (0x00, 0x02, "left", "right"):
			raise ValueError(f"side out of range (0x00, 0x02, \"left\", \"right\"): {side}")

		match side:
			case "left": side = 0x00
			case "right": side = 0x02

		packet = self._build_command(
			CommandType.J_COLOR,
			helpers.uint(side, 8),
			*colors,
			helpers.uint(fade_ms, 16)
		)

		response = self.send_response_command(packet)
		return response

	def light_portal(self, side: Literal[0x00, 0x02, "left", "right"], r: int, g: int, b: int) -> None:
		"""
		Send the Light (L) command to the Portal of Power. (No response; Traptanium Portal only)\n
		Set the LED colours of the chosen side in the Portal to a specified colour value.

		Args:
			side: The side to set the colour of. (0x00 = left, 0x02 = right).
			r: The red colour value.
			g: The green colour value.
			b: The blue colour value.
		"""
		colors = self._rgb_u8(r, g, b)

		if side not in (0x00, 0x02, "left", "right"):
			raise ValueError(f"side out of range (0x00, 0x02): {side}")

		match side:
			case "left": side = 0x00
			case "right": side = 0x02

		packet = self._build_command(
			CommandType.LIGHT,
			helpers.uint(side, 8),
			*colors
		)

		self.send_command(packet)

	def light_trap(self, brightness: int) -> None:
		"""
		Send the Light (L) command to the Portal of Power. (No response; Traptanium Portal only)\n
		Set the brightness of the Portal's Trap slot LED.\n
		NOTE: Trap slot LED only lights up if a figure is being read

		Args:
			brightness: The brightness to set the Trap slot LED to.
		"""
		packet = self._build_command(
			CommandType.LIGHT,
			helpers.uint(0x01, 8),
			helpers.uint(brightness, 8)
		)

		self.send_command(packet)

	def activate_speakers(self, do_activate: bool, retries: int = 1) -> Optional[bytes]:
		"""
		Send the Music (M) command to the Portal of Power. (Receives optional response; Traptanium Portal only)\n
		Activate or deactivate the Portal's speakers.

		Args:
			do_activate: Whether to activate or deactivate the speakers.
			retries: How many times to retry (-1 = infinite). Defaults to 1.

		Returns:
			Mirrors the command with addition of unknown range (0x00 to 0xFF) and constant 0x19.
		"""
		packet = self._build_command(
			CommandType.MUSIC,
			helpers.uint(do_activate, 8)
		)

		response = self.send_response_command(packet, timeout_sec=1, retries=retries)
		return response

	def query(self, figure_index: int, block_index: int) -> bytes:
		"""Send the QUERY command to the Portal of Power.
		Query the data at the specified figure and block.
		Receives response.

		Args:
			figure_index: The slot index of the figure to query.
			block_index: The index of the block to query.

		Returns:
			Mirrors the command with addition of figure/block data.
		"""
		if figure_index not in range (0x10):
			raise ValueError(f"figure_index out of range (0 to 15): {figure_index}")

		if block_index not in range(0x40):
			raise ValueError(f"block_index out of range (0 to 63): {block_index}")

		packet = self._build_command(
			CommandType.QUERY,
			helpers.uint(figure_index, 8),
			helpers.uint(block_index, 8)
		)

		response = self.send_response_command(packet)
		return response

	def ready(self) -> bytes:
		"""Send the READY command to the Portal of Power.
		Send the ready handshake with the Portal of Power.
		Receives response.

		Returns:
			Mirrors the command with addition of ranges (0x00, 0x01) and (0x00 to 0xFF) that identify the portal.
		"""
		packet = self._build_command(
			CommandType.READY
		)

		response = self.send_response_command(packet)
		return response

	def status(self) -> bytes:
		"""Send the STATUS command to the Portal of Power.
		Query the status of the Portal.
		Receives response.

		Returns:
			Mirrors the command with addition of the character status array, a byte-long counter,
			and a boolean whether the READY command has been sent beforehand.
		"""
		packet = self._build_command(
			CommandType.STATUS
		)

		response = self.send_response_command(packet)
		return response

	def write(self, figure_index: int, block_index: int, data: bytes) -> bytes:
		"""Send the WRITE command to the Portal of Power.
		Write data to the specified figure and block.
		Receives response.

		Args:
			figure_index: The slot index of the figure to write to.
			block_index: The index of the block to write to.
			data: The data to write to the figure/block.

		Returns:
			Mirrors the command character and block index, but not the figure index (0x00 instead).
			Written data is not mirrored.
		"""
		if figure_index not in range (0x10):
			raise ValueError(f"figure_index out of range (0 to 15): {figure_index}")

		if block_index not in range(0x40):
			raise ValueError(f"block_index out of range (0 to 63): {block_index}")

		if len(data) != 16:
			raise ValueError(f"data must be 16 bytes long: {len(data)}")

		packet = self._build_command(
			CommandType.WRITE,
			helpers.uint(figure_index + 0x10, 8),
			helpers.uint(block_index, 8),
			data
		)

		response = self.send_response_command(packet)
		return response