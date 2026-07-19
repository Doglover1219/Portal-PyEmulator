#:=---- Imports ----=:#
import time
import usb.core
import wave

from logging import Logger
from pathlib import Path
from threading import Event, Thread
from typing import Optional

#:=---- Helpers ----=:#
PACKET_SIZE = 64
PACKET_DELAY = 0.001
VOLUME_SCALE = 0.14
# reasonable value for 1.0 volume; reasonable max: 0.25 / VOLUME_SCALE. Absolute max: None;
# experiment however you like; you do you; you break everyone's eardrums with static, hard-clipped noise. Boo-hoo, you.

REQUIRED_CHANNELS = 1
REQUIRED_BITRATE_HZ = 8000
REQUIRED_BYTE_DEPTH = 2

#:=---- MusicHandler ----=:#
class MusicHandler:
	def __init__(self, logger: Logger, endpoint_out: usb.core.Endpoint) -> None:
		"""A handler to send raw audio data to the Portal via the interrupt endpoint.

		Args:
			logger (Logger): Logger object.
			endpoint_out (usb.core.Endpoint): Endpoint OUT object.
		"""
		self.logger = logger
		self.logger.info("Setting up MusicHandler...")

		self.endpoint_out = endpoint_out

		#:=---- Threading ----=:#
		self.thread: Optional[Thread] = None

		self.is_busy = Event()
		self.is_finished = Event()

		self.stop_event = Event()

	#:=---- Internal Helpers ----=:#
	def _check_file(self, filepath: Path) -> bool:
		"""Check if a file is supported to be played on the Portal of Power.
		(16-bit mono WAV audio at 8000Hz)

		Args:
			filepath (Path): The path to the file to check.

		Returns:
			bool: Whether the file can be played on the Portal.
		"""
		if not filepath.is_file():
			self.logger.debug(f"File {filepath} is not a file.")
			return False

		try:
			with wave.open(str(filepath), mode="rb") as f:
				channels = f.getnchannels()
				sample_width = f.getsampwidth()
				framerate = f.getframerate()
		except wave.Error:
			self.logger.debug(f"File {filepath} is not in WAV format.")
			return False

		if channels != REQUIRED_CHANNELS:
			self.logger.debug(f"File {filepath} does not have {REQUIRED_CHANNELS} channels. ({channels=})")
			return False

		if sample_width != REQUIRED_BYTE_DEPTH:
			self.logger.debug(f"File {filepath} is not {REQUIRED_BYTE_DEPTH*8}-bit. ({sample_width=})")
			return False

		if framerate != REQUIRED_BITRATE_HZ:
			self.logger.debug(f"File {filepath} is not {REQUIRED_BITRATE_HZ} Hz. ({framerate=})")
			return False

		return True

	def _play_loop(self, filepath: Path, volume: float = 1, start_s: float|int = 0, end_s: float|int = -1) -> None:
		volume = max(0, volume * VOLUME_SCALE)
		start_s = max(0, start_s)
		gain = volume ** 3

		with wave.open(str(filepath), "rb") as f:
			audio = f.readframes(f.getnframes())

		samples: bytearray = bytearray()

		for i in range(0, len(audio), REQUIRED_BYTE_DEPTH):
			sample = int.from_bytes(
				audio[i:i + REQUIRED_BYTE_DEPTH],
				byteorder="little",
				signed=True
			)

			sample = int(sample * gain)
			sample = max(-32768, min(sample, 32767))  # Int16 (-32768 to 32767)

			samples += sample.to_bytes(REQUIRED_BYTE_DEPTH, byteorder="little", signed=True)[::-1]

		if start_s > 0:
			start_byte = int(start_s * REQUIRED_BITRATE_HZ * REQUIRED_BYTE_DEPTH)
			samples = samples[start_byte:]

		if end_s > 0:
			end_s = max(0, end_s - start_s)
			end_byte = int(end_s * REQUIRED_BITRATE_HZ * REQUIRED_BYTE_DEPTH)
			samples = samples[:end_byte]

		self.is_busy.set()
		self.is_finished.clear()

		self.logger.info("Starting playback...")
		for i in range(0, len(samples), PACKET_SIZE):
			if self.stop_event.is_set():
				self.stop_event.clear()
				break

			packet = samples[i:i + PACKET_SIZE]

			while True:
				try:
					self.endpoint_out.write(packet)
					break
				except usb.core.USBTimeoutError:
					self.logger.debug("Packet timed out.")
					continue

			time.sleep(PACKET_DELAY)

		self.is_busy.clear()
		self.is_finished.set()

		self.logger.info("Playback finished.")

	#:=---- Public Methods ----=:#
	def play_file(self, filepath: Path, volume: float|int = 1, start_s: float|int = 0, end_s: float|int = -1) -> tuple[Event, Event]:
		"""Play an audio file through the Portal's speakers.

		Args:
			 filepath (Path): The path to the file to play (must contain 16-bit mono WAV audio at 8000Hz).
			 volume (float|int): The volume (on a scale from 0 to 1) at which to play the thing. Defaults to 1.
			 start_s (float|int): The time, in seconds, at which to cut the start of the track. Defaults to 0.
			 end_s (float|int): The time, in seconds, at which to cut the end of the track (-1 = end). Defaults to -1.

		Returns:
			tuple[Event, Event]: The is_busy event and the is_finished event, for easy access.

		Raises:
			ValueError: If the file does not contain 16-bit mono WAV audio at 8000Hz.
		"""
		self.logger.info(f"Playing file {filepath}...")

		if not self._check_file(filepath):
			raise ValueError(f"File {filepath} can not be played!")

		if self.is_busy.is_set():
			self.logger.warning("Tried to play audio file during ")

		self.thread = Thread(target=self._play_loop, args=(filepath, volume, start_s, end_s), daemon=True)
		self.thread.start()

		return self.is_busy, self.is_finished

	def play_file_and_wait(self, filepath: Path, volume: float|int = 1, start_s: float|int=0, end_s: float|int=-1, sleep_s: int = 1) -> None:
		"""Play an audio file through the Portal's speakers, and wait until the playback is done.

		Args:
			 filepath (Path): The path to the file to play (must contain 16-bit mono WAV audio at 8000Hz).
			 volume (float|int): The volume (on a scale from 0 to 1) at which to play the audio. Defaults to 1.
			 sleep_s (int): How long, in seconds, to wait until querying the next frame.
			 start_s (float|int): The time, in seconds, at which to cut the start of the track. Defaults to 0.
			 end_s (float|int): The time, in seconds, at which to cut the end of the track (-1 = end). Defaults to -1.

		Raises:
			ValueError: If the file does not contain 16-bit mono WAV audio at 8000Hz.
		"""
		self.play_file(filepath, volume=volume, start_s=start_s, end_s=end_s)

		self.is_busy.wait()
		self.is_finished.wait()

	def write(self, data: bytes) -> None:
		"""Mostly for direct game-to-portal relay communication.

		Args:
			data (bytes): The data to relay to the Portal.
		"""
		self.endpoint_out.write(data)

	#:=-- Helpers --=:#
	def get_busy(self) -> bool:
		"""Query whether music data is still being sent.

		Returns:
			bool: True if music data is still being sent, otherwise False.
		"""
		return self.is_busy.is_set()

	def get_finished(self) -> bool:
		"""Query whether music data is still being sent.

		Returns:
			bool: True if music data is not being sent, otherwise False.
		"""
		return self.is_finished.is_set()

	def stop_music(self) -> None:
		self.stop_event.set()

		if self.thread:
			self.thread.join()