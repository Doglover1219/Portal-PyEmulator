#:=---- Imports ----=:#
from enum import Flag, auto


#:=---- Export Folder Enum ----=:#
class ExportFolder(Flag):
	FIGURES  = auto()
	SETTINGS = auto()

	FULL     = FIGURES | SETTINGS