#:=---- Imports ----=:#
import zipfile

from logging import Logger
from pathlib import Path

#:=-- Local --=:#
import src.portal_pyemulator.helpers as helpers

from src.portal_pyemulator.storage.export_folder import ExportFolder


#:=---- Data Exporter Class ----=:#
class DataExporter:
	def __init__(self, logger: Logger) -> None:
		self.logger: Logger = logger
		self.logger.info("Setting up DataExporter...")

	def export_data(self, data_to_export: ExportFolder, output_path: Path) -> None:
		self.logger.info(f"Exporting data: {data_to_export.name}")
		relative_path: Path = helpers.get_data_path(".")

		filepaths: set[Path] = set()
		if ExportFolder.FIGURES in data_to_export:
			filepaths.update(self._get_figures())
		if ExportFolder.SETTINGS in data_to_export:
			filepaths.update(self._get_settings())

		output_path.parent.mkdir(parents=True, exist_ok=True)

		with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
			for filepath in filepaths:
				arcname = filepath.relative_to(relative_path)
				zipf.write(filepath, arcname)
				self.logger.info(f"Added {filepath} to archive")

	@staticmethod
	def _get_settings() -> list[Path]:
		path = helpers.get_data_path("settings.json")
		return [path] if path.exists() else []

	@staticmethod
	def _get_figures() -> list[Path]:
		root = helpers.get_data_path("figures")
		filepaths: list[Path] = []

		for filepath in root.rglob("*"):
			if filepath.is_file():
				filepaths.append(filepath)

		return filepaths

	def import_data(self, input_path: Path) -> None:
		...