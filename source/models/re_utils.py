def is_operand(ch):
	return ch.isalpha() or ch == '#' or ch == '&'

def is_capital(ch):
	begin = ord('A')
	end = ord('Z')
	at = ord(ch)
	return begin <= at <= end