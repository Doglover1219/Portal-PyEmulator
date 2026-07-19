#:=---- Imports ----=:#
from enum import IntEnum


#:=---- Command Type Enum ----=:#
class CommandType(IntEnum):
	ACTIVATE = ord("A")
	COLOR    = ord("C")
	J_COLOR  = ord("J")
	LIGHT    = ord("L")
	MUSIC    = ord("M")
	QUERY    = ord("Q")
	READY    = ord("R")
	STATUS   = ord("S")
	WRITE    = ord("W")