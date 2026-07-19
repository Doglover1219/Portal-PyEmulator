#:=---- Imports ----=:#
#:=-- Local --=:#
import portal_pyemulator.helpers as helpers


#:=---- Tests ----=:#
def test_bytes_to_str():
	inpt = bytes([
		ord("S"), 0x05, 0x03, 0x00, 0x00, 0x0F, 0x01, *([0x00] * 25)
	])
	expected_cmd_type = "S"
	expected = "S  05  03  00  00  0F  01" + ("  00" * 25)

	cmd_type, result = helpers.bytes_to_str(inpt)

	print(result)

	assert cmd_type == expected_cmd_type
	assert result == expected