#:=---- Imports ----=:#
import logging
import os
import sys

from pathlib import Path


#:=---- Helpers ----=:#
def get_loggers() -> tuple[logging.Logger, logging.Logger]:
	"""Get the main logger and the stream logger.

	Returns:
		tuple[logging.Logger, logging.Logger]: The main logger and the stream logger, respectively.
	"""
	logs_dir: Path = get_data_path("logs/")
	logs_dir.mkdir(parents=True, exist_ok=True)

	#:=-- Main Logger --=:#
	main_logger = logging.getLogger("portal_pyemulator:main")
	main_logger.setLevel(logging.DEBUG)

	# Formatter
	main_formatter = logging.Formatter(
		"[{name}][{asctime}/{levelname}][{filename}:{lineno}] {funcName}(): {message}",
		style="{"
	)

	# Stream Handler
	stream_handler = logging.StreamHandler(sys.stdout)
	stream_handler.setFormatter(main_formatter)

	main_logger.addHandler(stream_handler)

	# File Handler
	main_file_handler = logging.FileHandler(logs_dir / "latest.log", mode="w", encoding="utf-8")
	main_file_handler.setFormatter(main_formatter)

	main_logger.addHandler(main_file_handler)

	#:=-- Stream Logger --=:#
	stream_logger = logging.getLogger("portal_pyemulator:stream")
	stream_logger.setLevel(logging.DEBUG)

	# Formatter
	stream_formatter = logging.Formatter("[{asctime}/{levelname}] {message}", style="{")

	# File Handler
	stream_file_handler = logging.FileHandler(logs_dir / "stream.log", mode="w", encoding="utf-8")
	stream_file_handler.setFormatter(stream_formatter)
	stream_logger.addHandler(stream_file_handler)

	return main_logger, stream_logger

_MEIPASS: str | None = getattr(sys, "_MEIPASS", None)

def get_asset_path(relative_path: str | Path) -> Path:
	meipass_path: Path | None = Path(_MEIPASS) if _MEIPASS is not None else None
	if meipass_path is not None:
		base_path = meipass_path
	else:
		base_path = Path(__file__).parents[2]
	return base_path / "assets" / relative_path

def get_data_path(relative_path: str | Path) -> Path:
	appdata_dir: str | None = os.getenv("APPDATA")

	if appdata_dir is None:
		raise FileNotFoundError("Could not find environment variable %APPDATA%")
	appdata_path = Path(appdata_dir, "Portal PyEmulator")

	return appdata_path / relative_path

def bytes_to_str(data: bytes) -> tuple[str, str]:
	"""Convert raw portal output bytes to a human-readable output string.

	Returns:
		tuple[str, str]: The command type character, and the human-readable output string.
	"""
	result = []

	cmd_type = chr(data[0])

	result.append(cmd_type)
	result.extend(f"{byte:02x}".upper() for byte in data[1:])

	return cmd_type, "  ".join(result)

def uint(value: int, bit_length: int) -> bytes:
	if bit_length % 8 != 0:
		raise ValueError("Byte size must be a multiple of 8.")

	if bit_length < 0:
		raise ValueError(f"Value {value} cannot be represented as an unsigned integer; negative.")

	if value.bit_length() > bit_length:
		raise ValueError(f"Value {value} cannot be represented as an unsigned {bit_length}-bit integer; too large.")

	byte_length = bit_length // 8

	return value.to_bytes(byte_length, "little", signed=False)