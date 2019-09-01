"""
Fast packer and unpacker -- makes packing and unpacking with the struct module much faster and easier to use.
"""

from enum import Enum
import re
import struct
import inspect

__all__ = ["Endianness", "funpack", "fpack"]

class Endianness(Enum):
	"""
	Enum class for endianness of funpack operations.
	Avoids having to remember the characters.
	"""

	Native = '@'
	NativeNoAlign = '='
	Little = '<'
	Big = '>'
	Network = '!'

class fpack:
	"""
	Fast packing class.
	Uses the struct module that comes with Python and provided faster/easier access to packing.
	The endianness is supplied with each pack call and exposed via the Endian property.

	The pack functions provided are named based on size, rather than an arbitrary character code.
	Note that not all characters have shortcut functions (mostly because I don't use them).

	Lastly, you can call Pack() directly with any format string you need to use.

	Each call adds data to an internal list.
	Access the Data property to get the resulting binary data string that contains
	 all of the data supplied to the calls on this object.
	Further pack arguments can be called if desired.
	"""

	def __init__(self, endian=Endianness.Native):
		self._buffer = []
		self.Endian = endian

	@property
	def Endian(self):
		"""
		Gets the endianness in which data is unpacked.
		"""
		return self._endian

	@Endian.setter
	def Endian(self, v):
		"""
		Sets the endianness.
		"""

		if type(v) == str:
			if v == Endianness.Native.value:				v = Endianness.Native
			elif v == Endianness.NativeNoAlign.value:		v = Endianness.NativeNoAlign
			elif v == Endianness.Little.value:				v = Endianness.Little
			elif v == Endianness.Big.value:					v = Endianness.Big
			elif v == Endianness.Network.value:				v = Endianness.Network

			elif v.lower() == 'native':						v = Endianness.Native
			elif v.lower() == 'nativenoalign':				v = Endianness.NativeNoAlign
			elif v.lower() == 'little':						v = Endianness.Little
			elif v.lower() == 'big':						v = Endianness.Big
			elif v.lower() == 'net':						v = Endianness.Network
			elif v.lower() == 'network':					v = Endianness.Network

			else:
				raise ValueError("Unrecognized v value '%s' expected @, =, <, >, or !, or case-insensitive names native, nativenoalign, little, big, net, or network" % v)

		elif type(v) == Endianness:
			# Nothing to do
			pass
		else:
			raise TypeError("Unrecognized type for v '%s' expected Endianness or string" % type(v))

		self._endian = v

	@property
	def Data(self):
		"""
		Gets the resulting total buffer output of binary data.
		"""

		return b''.join(self._buffer)

	def Pack(self, fmt, objs):
		"""
		Pack wraps struct.pack by using the internal offset counter and the endian specified in the initializer.
		"""

		e = self.Endian.value

		# Pack
		ret = struct.pack(e + fmt, *objs)

		# Add to buffer
		self._buffer.append(ret)

		# Return unpacked data
		return ret

	# ----------------------------------------
	# Other

	def pad(self, times=1):
		"""
		"Write" padding bytes.
		None is returned always for any amount of @times.
		"""
		self.Pack('x' * times, tuple())
		return None

	# ----------------------------------------
	# Unsigned

	def u8(self, *vals):
		"""
		Puts unsigned 8-bit (1 byte) values.
		"""
		times = len(vals)
		return self.Pack('B'*times, [int(_) for _ in vals])

	def u16(self, *vals):
		"""
		Puts unsigned 16-bit (2 bytes) values.
		"""
		times = len(vals)
		return self.Pack('H'*times, [int(_) for _ in vals])

	def u32(self, *vals):
		"""
		Puts unsigned 32-bit (4 bytes) values.
		"""
		times = len(vals)
		return self.Pack('I'*times, [int(_) for _ in vals])

	def u64(self, *vals):
		"""
		Puts unsigned 64-bit (8 bytes) values.
		"""
		times = len(vals)
		return self.Pack('Q'*times, [int(_) for _ in vals])

	# ----------------------------------------
	# Signed

	def s8(self, *vals):
		"""
		Puts signed 8-bit (1 byte) values.
		"""
		times = len(vals)
		return self.Pack('b'*times, [int(_) for _ in vals])

	def s16(self, *vals):
		"""
		Puts signed 16-bit (2 bytes) values.
		"""
		times = len(vals)
		return self.Pack('h'*times, [int(_) for _ in vals])

	def s32(self, *vals):
		"""
		Puts signed 32-bit (4 bytes) values.
		"""
		times = len(vals)
		return self.Pack('i'*times, [int(_) for _ in vals])

	def s64(self, *vals):
		"""
		Puts signed 64-bit (8 bytes) values.
		"""
		times = len(vals)
		return self.Pack('q'*times, [int(_) for _ in vals])

	# ----------------------------------------
	# Float

	def f32(self, *vals):
		"""
		Puts a 32-bit float value ("float"); 64-bit is a "double" so use f64().
		"""
		times = len(vals)
		return self.Pack('f'*times, [float(_) for _ in vals])

	def f64(self, *vals):
		"""
		Puts a 64-bit float value ("float"); 32-bit is a "float" so use f32().
		"""
		times = len(vals)
		return self.Pack('d'*times, [float(_) for _ in vals])

	# ----------------------------------------
	# puts a binary string of data

	def bytes(self, *vals):
		"""
		Puts a binary string of bytes.
		"""
		ret = []
		for v in vals:
			z = self.Pack('%ds' % len(v), [v])
			ret.append(z)
		return ret

	def string(self, encoding, *vals):
		"""
		Puts a text string as encoded bytes.
		@encoding is the text encoding used.
		"""
		ret = []
		for v in vals:
			vv = v.encode(encoding)
			z = self.Pack('%ds' % len(vv), [vv])
			ret.append(z)
		return ret

	def string_ascii(self, *vals):
		"""
		Puts an ASCII text string as encoded bytes.
		This is a convenience function to string()
		@encoding is the text encoding used.
		"""
		return self.string('ascii', *vals)

	def string_utf8(self, *vals):
		"""
		Puts an UTF-8 text string as encoded bytes.
		This is a convenience function to string()
		@encoding is the text encoding used.
		"""
		return self.string('utf-8', *vals)

	def string_utf16(self, *vals):
		"""
		Puts an UTF-16 text string as encoded bytes.
		This is a convenience function to string()
		@encoding is the text encoding used.
		"""
		return self.string('utf-16', *vals)

	def string_utf32(self, *vals):
		"""
		Puts an UTF-32 text string as encoded bytes.
		This is a convenience function to string()
		@encoding is the text encoding used.
		"""
		return self.string('utf-32', *vals)

	# ----------------------------------------
	# Length-driven write

	def _lendat(self, vals):
		"""
		Root function that looks at the calling function name to determine the parameters.
		Accepting function name of the format "u8len_u8dat"
		 1) Type of length identifier (u=unsigned, signed not accepted as it makes no sense)
		 2) Bit length of length identifier (8,16,32,64)
		 3) Type of data identifier (u=unsigned, s=signed)
		 4) Bit length of data (8,16,32,64)
		"""

		# Length of data to encode
		ln = len(vals)

		# Get function name of calling function ([0] is current frame, [1] is calling frame)
		fname = inspect.stack()[1].function

		# Match format of function name
		r = re.match("^([a-z])([0-9]{1,2})len_([a-z])([0-9]{1,2})dat$", fname)
		if r is None:
			raise Exception("Function name '%s' unrecognized" % fname)

		# Convert lengths (8,16,32,64) into numbers
		lntyp = int(r.group(2))
		valstyp = int(r.group(4))

		# (1)
		# Match length type (u = unsigned)
		if r.group(1) != 'u':
			raise Exception("Unrecognized array length type: '%s'" % r.group(1))

		# (2)
		if lntyp == 8:
			r1 = self.u8(ln)
		elif lntyp == 16:
			r1 = self.u16(ln)
		elif lntyp == 32:
			r1 = self.u32(ln)
		elif lntyp == 64:
			r1 = self.u64(ln)
		else:
			raise ValueError("Unrecognized length type: %d" % lntyp)


		# (3)
		if r.group(3) == 'u':
			signed = False
		elif r.group(3) == 's':
			signed = True
		else:
			raise Exception("Unrecognized value length type: '%s'" % r.group(2))

		# Ensure length is appropriate
		if ln >= 2**lntyp:
			raise ValueError("Cannot encode more than %d items in an %d-bit length; got %d values" % (2**lntyp-1, lntyp, ln))

		# (4)
		# Encode values
		if valstyp == 8:
			if signed:
				r2 = self.s8(*vals)
			else:
				r2 = self.u8(*vals)
		elif valstyp == 16:
			if signed:
				r2 = self.s16(*vals)
			else:
				r2 = self.u16(*vals)
		elif valstyp == 32:
			if signed:
				r2 = self.s32(*vals)
			else:
				r2 = self.u32(*vals)
		elif valstyp == 64:
			if signed:
				r2 = self.s64(*vals)
			else:
				r2 = self.u64(*vals)
		else:
			raise NotImplementedError

		return (r1,r2)

	def u8len_u8dat(self, *vals):
		return self._lendat(vals)
	def u8len_u16dat(self, *vals):
		return self._lendat(vals)
	def u8len_u32dat(self, *vals):
		return self._lendat(vals)
	def u8len_u64dat(self, *vals):
		return self._lendat(vals)

	def u8len_s8dat(self, *vals):
		return self._lendat(vals)
	def u8len_s16dat(self, *vals):
		return self._lendat(vals)
	def u8len_s32dat(self, *vals):
		return self._lendat(vals)
	def u8len_s64dat(self, *vals):
		return self._lendat(vals)



	def u16len_u8dat(self, *vals):
		return self._lendat(vals)
	def u16len_u16dat(self, *vals):
		return self._lendat(vals)
	def u16len_u32dat(self, *vals):
		return self._lendat(vals)
	def u16len_u64dat(self, *vals):
		return self._lendat(vals)

	def u16len_s8dat(self, *vals):
		return self._lendat(vals)
	def u16len_s16dat(self, *vals):
		return self._lendat(vals)
	def u16len_s32dat(self, *vals):
		return self._lendat(vals)
	def u16len_s64dat(self, *vals):
		return self._lendat(vals)



	def u32len_u8dat(self, *vals):
		return self._lendat(vals)
	def u32len_u16dat(self, *vals):
		return self._lendat(vals)
	def u32len_u32dat(self, *vals):
		return self._lendat(vals)
	def u32len_u64dat(self, *vals):
		return self._lendat(vals)

	def u32len_s8dat(self, *vals):
		return self._lendat(vals)
	def u32len_s16dat(self, *vals):
		return self._lendat(vals)
	def u32len_s32dat(self, *vals):
		return self._lendat(vals)
	def u32len_s64dat(self, *vals):
		return self._lendat(vals)



	def u64len_u8dat(self, *vals):
		return self._lendat(vals)
	def u64len_u16dat(self, *vals):
		return self._lendat(vals)
	def u64len_u32dat(self, *vals):
		return self._lendat(vals)
	def u64len_u64dat(self, *vals):
		return self._lendat(vals)

	def u64len_s8dat(self, *vals):
		return self._lendat(vals)
	def u64len_s16dat(self, *vals):
		return self._lendat(vals)
	def u64len_s32dat(self, *vals):
		return self._lendat(vals)
	def u64len_s64dat(self, *vals):
		return self._lendat(vals)


class funpack:
	"""
	Fast unpacker class.
	Uses the struct module that comes with Python and provided faster/easier access to unpacking.
	Offset within the data source is maintained within and exposed via the Offset property.
	The endianness is supplied with each unpack call and exposed via the Endian property.
	Both the offset and endian can be changed at any time.

	The unpack functions provided are named based on size, rather than an arbitrary character code.
	Note that not all characters have shortcut functions (mostly because I don't use them).

	Lastly, you can call Unpack() directly with any format string you need to use.
	"""

	def __init__(self, src, endian=Endianness.Native, offset=0):
		"""
		Initialize the fast unpacker with data source @src and use the endian @endian for all unpacks.
		@src is any type that struct.unpack() accepts.
		@endian can be either a character (@, =, <, >, or !), case-insentivie names (native, nativenoalign, little, big, net, or network) or an Endianness enum value.
		@offset is the default offset to start unpacking from.
		"""

		self._src = src
		self.Offset = offset
		self.Endian = endian

	@property
	def Src(self):
		"""
		Gets the data source the unpacking is performed on.
		"""
		return self._src

	@property
	def Offset(self):
		"""
		Gets the current offset within the data source.
		"""
		return self._offset

	@Offset.setter
	def Offset(self, v):
		"""
		Sets the offset within the data source.
		"""
		self._offset = v

	@property
	def Endian(self):
		"""
		Gets the endianness in which data is unpacked.
		"""
		return self._endian

	@Endian.setter
	def Endian(self, v):
		"""
		Sets the endianness.
		"""

		if type(v) == str:
			if v == Endianness.Native.value:				v = Endianness.Native
			elif v == Endianness.NativeNoAlign.value:		v = Endianness.NativeNoAlign
			elif v == Endianness.Little.value:				v = Endianness.Little
			elif v == Endianness.Big.value:					v = Endianness.Big
			elif v == Endianness.Network.value:				v = Endianness.Network

			elif v.lower() == 'native':						v = Endianness.Native
			elif v.lower() == 'nativenoalign':				v = Endianness.NativeNoAlign
			elif v.lower() == 'little':						v = Endianness.Little
			elif v.lower() == 'big':						v = Endianness.Big
			elif v.lower() == 'net':						v = Endianness.Network
			elif v.lower() == 'network':					v = Endianness.Network

			else:
				raise ValueError("Unrecognized v value '%s' expected @, =, <, >, or !, or case-insensitive names native, nativenoalign, little, big, net, or network" % v)

		elif type(v) == Endianness:
			# Nothing to do
			pass
		else:
			raise TypeError("Unrecognized type for v '%s' expected Endianness or string" % type(v))

		self._endian = v

	def Unpack(self, fmt):
		"""
		Unpack wraps struct.unpack by using the internal offset counter and the endian specified in the initializer.
		"""

		e = self.Endian.value

		# Get the size of the format string
		sz = struct.calcsize(e + fmt)

		# Unpack
		ret = struct.unpack_from(e + fmt, self._src, self.Offset)

		# Increment offset
		self.Offset += sz

		# Return unpacked data
		return ret

	# --------------------------------------------------------------------------------
	# --------------------------------------------------------------------------------
	# Shortcut functions

	def _short(self, char, times):
		"""Shortcut function intended to be used internally only."""
		if times == 1:
			return self.Unpack(char)[0]
		else:
			return self.Unpack(char * times)

	# ----------------------------------------
	# Other

	def pad(self, times=1):
		"""
		"Read" padding bytes, which means nothing is actually read.
		None is returned always for any amount of @times.
		"""
		self.Unpack('x' * times)
		return None

	# ----------------------------------------
	# Unsigned

	def u8(self, times=1):
		"""
		Gets an unsigned 8-bit (1 byte) value.
		If @times is one, then the integer is returned.
		If @times is not one, then a tuple of integers is returned.
		"""
		return self._short('B', times)

	def u16(self, times=1):
		"""
		Gets an unsigned 16-bit (2 bytes) value.
		If @times is one, then the integer is returned.
		If @times is not one, then a tuple of integers is returned.
		"""
		return self._short('H', times)

	def u32(self, times=1):
		"""
		Gets an unsigned 32-bit (4 bytes) value.
		If @times is one, then the integer is returned.
		If @times is not one, then a tuple of integers is returned.
		"""
		return self._short('I', times)

	def u64(self, times=1):
		"""
		Gets an unsigned 64-bit (8 bytes) value.
		If @times is one, then the integer is returned.
		If @times is not one, then a tuple of integers is returned.
		"""
		return self._short('Q', times)

	# ----------------------------------------
	# Signed

	def s8(self, times=1):
		"""
		Gets a signed 8-bit (1 byte) value.
		If @times is one, then the integer is returned.
		If @times is not one, then a tuple of integers is returned.
		"""
		return self._short('b', times)

	def s16(self, times=1):
		"""
		Gets a signed 16-bit (2 bytes) value.
		If @times is one, then the integer is returned.
		If @times is not one, then a tuple of integers is returned.
		"""
		return self._short('h', times)

	def s32(self, times=1):
		"""
		Gets a signed 32-bit (4 bytes) value.
		If @times is one, then the integer is returned.
		If @times is not one, then a tuple of integers is returned.
		"""
		return self._short('i', times)

	def s64(self, times=1):
		"""
		Gets a signed 64-bit (8 bytes) value.
		If @times is one, then the integer is returned.
		If @times is not one, then a tuple of integers is returned.
		"""
		return self._short('q', times)

	# ----------------------------------------
	# Float

	def f32(self, times=1):
		"""
		Gets a 32-bit float value ("float"); 64-bit is a "double" so use f64().
		If @times is one, then the integer is returned.
		If @times is not one, then a tuple of integers is returned.
		"""
		return self._short('f', times)

	def f64(self, times=1):
		"""
		Gets a 64-bit float value ("double"); 32-bit is a "float" so use f32().
		If @times is one, then the integer is returned.
		If @times is not one, then a tuple of integers is returned.
		"""
		return self._short('d', times)

	# ----------------------------------------
	# Gets a binary string of data

	def bytes(self, ln):
		"""
		Gets a binary string of bytes.
		@ln is number of bytes to return as a bytes string.
		"""
		return self.Unpack('%ds' % ln)[0]

	def string(self, ln, encoding):
		"""
		Gets a binary string of bytes and then decodes them as a string.
		@ln is number of bytes to unpack (not the number of characters).
		@encoding is the text encoding used.
		"""
		return self.bytes(ln).decode(encoding)

	def string_ascii(self, ln):
		"""
		Gets a binary string of bytes and then decodes them as a ASCII text string.
		This is a convenience function to string().
		@ln is number of bytes to unpack (not the number of characters).
		"""
		return self.bytes(ln).decode('ascii')

	def string_utf8(self, ln):
		"""
		Gets a binary string of bytes and then decodes them as a UTF-8 text string.
		This is a convenience function to string().
		@ln is number of bytes to unpack (not the number of characters).
		"""
		return self.bytes(ln).decode('utf-8')

	def string_utf16(self, ln):
		"""
		Gets a binary string of bytes and then decodes them as a UTF-16 text string.
		This is a convenience function to string().
		@ln is number of bytes to unpack (not the number of characters).
		"""
		return self.bytes(ln).decode('utf-16')

	def string_utf32(self, ln):
		"""
		Gets a binary string of bytes and then decodes them as a UTF-32 text string.
		This is a convenience function to string().
		@ln is number of bytes to unpack (not the number of characters).
		"""
		return self.bytes(ln).decode('utf-32')

	# ----------------------------------------
	# Length-driven reads

	# u8 length, unsigned data

	def u8len_u8dat(self):
		"""
		Reads an unsigned 8-bit value as a length and that many unsigned 8-bit values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u8()
		return self.u8(ln)

	def u8len_u16dat(self):
		"""
		Reads an unsigned 8-bit value as a length and that many unsigned 16-bit values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u8()
		return self.u16(ln)

	def u8len_u32dat(self):
		"""
		Reads an unsigned 8-bit value as a length and that many unsigned 32-bit values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u8()
		return self.u32(ln)

	def u8len_u64dat(self):
		"""
		Reads an unsigned 8-bit value as a length and that many unsigned 64-bit values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u8()
		return self.u64(ln)

	# ---------
	# u8 length, signed data

	def u8len_s8dat(self):
		"""
		Reads an unsigned 8-bit value as a length and that many signed 8-bit values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u8()
		return self.s8(ln)

	def u8len_s16dat(self):
		"""
		Reads an unsigned 8-bit value as a length and that many signed 16-bit values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u8()
		return self.s16(ln)

	def u8len_s32dat(self):
		"""
		Reads an unsigned 8-bit value as a length and that many signed 32-bit values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u8()
		return self.s32(ln)

	def u8len_s64dat(self):
		"""
		Reads an unsigned 8-bit value as a length and that many signed 64-bit values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u8()
		return self.s64(ln)

	# ---------
	# u16 length, unsigned data

	def u16len_u8dat(self):
		"""
		Reads an unsigned 16-bit value as a length and that many unsigned 8-bit values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u16()
		return self.u8(ln)

	def u16len_u16dat(self):
		"""
		Reads an unsigned 16-bit value as a length and that many unsigned 16-bit values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u16()
		return self.u16(ln)

	def u16len_u32dat(self):
		"""
		Reads an unsigned 16-bit value as a length and that many unsigned 32-bit values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u16()
		return self.u32(ln)

	def u16len_u64dat(self):
		"""
		Reads an unsigned 16-bit value as a length and that many unsigned 64-bit values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u16()
		return self.u64(ln)

	# ---------
	# u16 length, signed data

	def u16len_s8dat(self):
		"""
		Reads an unsigned 16-bit value as a length and that many signed 8-bit values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u16()
		return self.s8(ln)

	def u16len_s16dat(self):
		"""
		Reads an unsigned 16-bit value as a length and that many signed 16-bit values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u16()
		return self.s16(ln)

	def u16len_s32dat(self):
		"""
		Reads an unsigned 16-bit value as a length and that many signed 32-bit values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u16()
		return self.s32(ln)

	def u16len_s64dat(self):
		"""
		Reads an unsigned 16-bit value as a length and that many signed 64-bit values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u16()
		return self.s64(ln)

	# ---------
	# u8 and u16 length, 32-bit float data

	def u8len_f32dat(self):
		"""
		Reads an unsigned 8-bit value as a length and that many 32-bit float values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u8()
		return self.f32(ln)

	def u8len_f64dat(self):
		"""
		Reads an unsigned 8-bit value as a length and that many 64-bit float values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u8()
		return self.f64(ln)

	def u16len_f32dat(self):
		"""
		Reads an unsigned 16-bit value as a length and that many 32-bit float values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u16()
		return self.f32(ln)

	def u16len_f64dat(self):
		"""
		Reads an unsigned 16-bit value as a length and that many 64-bit float values are read and returned.
		The length is not returned, but if you need it you should just make the two calls yourself.
		"""
		ln = self.u16()
		return self.f64(ln)

	# ----------------------------------------
	# Offset jumps

	def u8jump(self, multiplier=1, tweak=0):
		"""
		Read an unsigned 8-bit value, and jump offset by that much.
		The @multiplier is a multiple of the jump value.
		Also, @tweak may can tweak the jumped offset (after multiplying by @multiplier).
		"""
		ln = self.u8()
		self.Offset += multiplier*ln + tweak
		return ln

	def u16jump(self, multiplier=1, tweak=0):
		"""
		Read an unsigned 16-bit value, and jump offset by that much.
		The @multiplier is a multiple of the jump value.
		Also, @tweak may can tweak the jumped offset (after multiplying by @multiplier).
		"""
		ln = self.u16()
		self.Offset += multiplier*ln + tweak
		return ln

	def u32jump(self, multiplier=1, tweak=0):
		"""
		Read an unsigned 32-bit value, and jump offset by that much.
		The @multiplier is a multiple of the jump value.
		Also, @tweak may can tweak the jumped offset (after multiplying by @multiplier).
		"""
		ln = self.u32()
		self.Offset += multiplier*ln + tweak
		return ln

	def u64jump(self, multiplier=1, tweak=0):
		"""
		Read an unsigned 64-bit value, and jump offset by that much.
		The @multiplier is a multiple of the jump value.
		Also, @tweak may can tweak the jumped offset (after multiplying by @multiplier).
		"""
		ln = self.u64()
		self.Offset += multiplier*ln + tweak
		return ln




def test():
	test_fpack()
	test_funpack()

	print("All is good")

def test_fpack():
	f = fpack(Endianness.Little)
	f.u8(5)
	assert(f.Data == struct.pack("<B", 5))

	f = fpack(Endianness.Little)
	f.s8(5)
	assert(f.Data == struct.pack("<b", 5))

	f = fpack()
	f.u8(5, 10, 20)
	assert(f.Data == struct.pack("<BBB", 5, 10, 20))
	f = fpack()
	f.u16(5, 10, 20)
	assert(f.Data == struct.pack("<HHH", 5, 10, 20))
	f = fpack()
	f.u32(5, 10, 20)
	assert(f.Data == struct.pack("<III", 5, 10, 20))
	f = fpack()
	f.u64(5, 10, 20)
	assert(f.Data == struct.pack("<QQQ", 5, 10, 20))

	f = fpack()
	f.s8(5, 10, 20)
	assert(f.Data == struct.pack("<bbb", 5, 10, 20))
	f = fpack()
	f.s16(5, 10, 20)
	assert(f.Data == struct.pack("<hhh", 5, 10, 20))
	f = fpack()
	f.s32(5, 10, 20)
	assert(f.Data == struct.pack("<iii", 5, 10, 20))
	f = fpack()
	f.s64(5, 10, 20)
	assert(f.Data == struct.pack("<qqq", 5, 10, 20))

	f = fpack()
	f.string("ascii", "Hello")
	assert(f.Data == struct.pack("<5s", "Hello".encode('ascii')))


	f = fpack(Endianness.Big)
	f.u8(*list(range(0, 10)))
	f.u16(*list(range(10, 20)))
	f.u32(*list(range(20, 30)))
	f.u64(*list(range(30, 40)))
	f.f32(1.25)
	f.f64(2.5)
	f.f32(3.75)

	dat = f.Data

	f = funpack(dat, endian=Endianness.Big)

	# ------------- u8 -------------
	assert(f.u8() == 0)
	assert(f.pad() == None)
	assert(f.u8(2) == (2,3))
	assert(f.u8(2) == (4,5))
	assert(f.u8() == 6)
	assert(f.u8() == 7)
	assert(f.u8(2) == (8,9))

	# ------------- u16 -------------
	assert(f.u16() == 10)
	assert(f.pad(2) == None)
	assert(f.u16(2) == (12,13))
	assert(f.u16(2) == (14,15))
	assert(f.u16() == 16)
	assert(f.u16() == 17)
	assert(f.u16(2) == (18,19))

	# ------------- u32 -------------
	assert(f.u32() == 20)
	assert(f.pad(4) == None)
	assert(f.u32(2) == (22,23))
	assert(f.u32(2) == (24,25))
	assert(f.u32() == 26)
	assert(f.u32() == 27)
	assert(f.u32(2) == (28,29))

	# ------------- u64 -------------
	assert(f.u64() == 30)
	assert(f.pad(8) == None)
	assert(f.u64(2) == (32,33))
	assert(f.u64(2) == (34,35))
	assert(f.u64() == 36)
	assert(f.u64() == 37)
	assert(f.u64(2) == (38,39))

	# ------------- float -------------

	assert(f.f32() == 1.25)
	assert(f.f64() == 2.5)
	assert(f.f32() == 3.75)

	def lenpack8(ln, char):
		return struct.pack(Endianness.Big.value + "B" + char*ln, ln, *(list(range(ln))))
	def lenpack16(ln, char):
		return struct.pack(Endianness.Big.value + "H" + char*ln, ln, *(list(range(ln))))
	def lenpack32(ln, char):
		return struct.pack(Endianness.Big.value + "I" + char*ln, ln, *(list(range(ln))))
	def lenpack64(ln, char):
		return struct.pack(Endianness.Big.value + "Q" + char*ln, ln, *(list(range(ln))))

	f = fpack(Endianness.Big)
	f.u8len_u8dat(*list(range(50)))
	assert(f.Data == lenpack8(50, "B"))

	f = fpack(Endianness.Big)
	f.u8len_u16dat(*list(range(50)))
	assert(f.Data == lenpack8(50, "H"))

	f = fpack(Endianness.Big)
	f.u8len_u32dat(*list(range(50)))
	assert(f.Data == lenpack8(50, "I"))

	f = fpack(Endianness.Big)
	f.u8len_u64dat(*list(range(50)))
	assert(f.Data == lenpack8(50, "Q"))


	f = fpack(Endianness.Big)
	f.u16len_u8dat(*list(range(50)))
	assert(f.Data == lenpack16(50, "B"))

	f = fpack(Endianness.Big)
	f.u16len_u16dat(*list(range(50)))
	assert(f.Data == lenpack16(50, "H"))

	f = fpack(Endianness.Big)
	f.u16len_u32dat(*list(range(50)))
	assert(f.Data == lenpack16(50, "I"))

	f = fpack(Endianness.Big)
	f.u16len_u64dat(*list(range(50)))
	assert(f.Data == lenpack16(50, "Q"))


	f = fpack(Endianness.Big)
	f.u32len_u8dat(*list(range(50)))
	assert(f.Data == lenpack32(50, "B"))

	f = fpack(Endianness.Big)
	f.u32len_u16dat(*list(range(50)))
	assert(f.Data == lenpack32(50, "H"))

	f = fpack(Endianness.Big)
	f.u32len_u32dat(*list(range(50)))
	assert(f.Data == lenpack32(50, "I"))

	f = fpack(Endianness.Big)
	f.u32len_u64dat(*list(range(50)))
	assert(f.Data == lenpack32(50, "Q"))


	f = fpack(Endianness.Big)
	f.u64len_u8dat(*list(range(50)))
	assert(f.Data == lenpack64(50, "B"))

	f = fpack(Endianness.Big)
	f.u64len_u16dat(*list(range(50)))
	assert(f.Data == lenpack64(50, "H"))

	f = fpack(Endianness.Big)
	f.u64len_u32dat(*list(range(50)))
	assert(f.Data == lenpack64(50, "I"))

	f = fpack(Endianness.Big)
	f.u64len_u64dat(*list(range(50)))
	assert(f.Data == lenpack64(50, "Q"))


def test_funpack():
	dat = struct.pack(Endianness.Big.value + "B"*10 + "H"*10 + "I"*10 + "Q"*10 + "fdf", *(list(range(40)) + [1.25, 2.5, 3.75]))

	f = funpack(dat, endian=Endianness.Big)

	# ------------- u8 -------------
	assert(f.u8() == 0)
	assert(f.pad() == None)
	assert(f.u8(2) == (2,3))
	assert(f.u8(2) == (4,5))
	assert(f.u8() == 6)
	assert(f.u8() == 7)
	assert(f.u8(2) == (8,9))

	# ------------- u16 -------------
	assert(f.u16() == 10)
	assert(f.pad(2) == None)
	assert(f.u16(2) == (12,13))
	assert(f.u16(2) == (14,15))
	assert(f.u16() == 16)
	assert(f.u16() == 17)
	assert(f.u16(2) == (18,19))

	# ------------- u32 -------------
	assert(f.u32() == 20)
	assert(f.pad(4) == None)
	assert(f.u32(2) == (22,23))
	assert(f.u32(2) == (24,25))
	assert(f.u32() == 26)
	assert(f.u32() == 27)
	assert(f.u32(2) == (28,29))

	# ------------- u64 -------------
	assert(f.u64() == 30)
	assert(f.pad(8) == None)
	assert(f.u64(2) == (32,33))
	assert(f.u64(2) == (34,35))
	assert(f.u64() == 36)
	assert(f.u64() == 37)
	assert(f.u64(2) == (38,39))

	# ------------- float -------------

	assert(f.f32() == 1.25)
	assert(f.f64() == 2.5)
	assert(f.f32() == 3.75)

	def lenpack(ln, char):
		return struct.pack(Endianness.Big.value + "B" + char*ln, ln, *(list(range(ln))))

	# ------------- len 10, 8-bit -------------
	f = funpack(lenpack(10, "B"), endian=Endianness.Big)
	assert(f.u8len_u8dat() == (0,1,2,3,4,5,6,7,8,9))

	# ------------- len 20, 8-bit -------------
	f = funpack(lenpack(20, "B"), endian=Endianness.Big)
	assert(f.u8len_u8dat() == (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19))

	# ------------- len 15, 16-bit -------------
	f = funpack(lenpack(15, "H"), endian=Endianness.Big)
	assert(f.u8len_u16dat() == (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14))

	# ------------- len 30, 32-bit -------------
	f = funpack(lenpack(30, "I"), endian=Endianness.Big)
	assert(f.u8len_u32dat() == (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29))


	def jumppack(ln, jmp, char):
		return struct.pack(Endianness.Big.value + "B" + char*ln, *([jmp] + list(range(ln))))

	# ------------- 8-bit jump 3 in 40 -------------
	f = funpack(jumppack(50, 3, "B"), endian=Endianness.Big)
	assert(f.u8jump(multiplier=1) == 3)
	assert(f.u8() == 3)

	# ------------- 16-bit jump 3 in 40 -------------
	f = funpack(jumppack(50, 3, "H"), endian=Endianness.Big)
	assert(f.u8jump(multiplier=2) == 3)
	assert(f.u16() == 3)

	# ------------- 32-bit jump 3 in 40 -------------
	f = funpack(jumppack(50, 3, "I"), endian=Endianness.Big)
	assert(f.u8jump(multiplier=4) == 3)
	assert(f.u32() == 3)

	# ------------- 64-bit jump 3 in 40 -------------
	f = funpack(jumppack(50, 3, "Q"), endian=Endianness.Big)
	assert(f.u8jump(multiplier=8) == 3)
	assert(f.u64() == 3)

	# ------------- bytes -------------
	z = "hello world, I am Taco!"
	f = funpack(z.encode('ascii'), endian=Endianness.Big)
	assert(f.bytes(5) == z[0:5].encode('ascii'))
	assert(f.bytes(1) == z[5].encode('ascii'))
	assert(f.bytes(5) == z[6:11].encode('ascii'))
	assert(f.bytes(12) == z[11:].encode('ascii'))

	# Try various language encodings to make sure they all work fine
	for enc in ['ascii', 'utf-7', 'utf-8', 'utf-16', 'utf-32', 'latin_1']:
		y = z.encode(enc)
		f = funpack(y)
		assert(f.string(len(y), enc) == z)


if __name__ == '__main__':
	test()

