"""
Fast unpacker -- makes unpacking with struct module much faster and easier to use.
"""

from enum import Enum
import struct

__all__ = ["Endianness", "funpack"]

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

class funpack:
	"""
	Fast unpacker class.
	Uses the struct module that comes with Python and provided faster/easier access to unpacking.
	Offset within the data source is maintained within and exposed via the Offset property.
	The endianness is supplied with each unpack call and exposed via the Endian property..
	Both the offset and endian can be changed at any time.

	The unpack functions provided are named based on size, rather than an arbitrary character code.
	Note that not all characters have shortcut functions (mostly because I don't use them).

	Lastly, you can call Unpack() directly with any format string you need to use.
	"""

	def __init__(self, src, endian=Endianness.Native, offset=0):
		"""
		Initialize the fast unpacker with data source @src and use the endian @endian for all unpacks.
		@src is any type that struct.unpack() accepts.
		@endian can be either a character (@, =, <, >, or !) or an Endianness enum value.
		@offset is the default offset to start unpacking from.
		"""

		if type(endian) == str:
			if endian == Endianness.Native.value:			endian = Endianness.Native
			elif endian == Endianness.NativeNoAlign.value:	endian = Endianness.NativeNoAlign
			elif endian == Endianness.Little.value:			endian = Endianness.Little
			elif endian == Endianness.Big.value:			endian = Endianness.Big
			elif endian == Endianness.Network.value:		endian = Endianness.Network
			else:
				raise ValueError("Unrecognized endian value '%s' expected @, =, <, >, or !" % endian)

		elif type(endian) == Endianness:
			# Nothing to do
			pass
		else:
			raise TypeError("Unrecognized type for endian '%s' expected Endianness or string" % type(endian))

		self._src = src
		self._offset = offset
		self.Endian = endian

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

