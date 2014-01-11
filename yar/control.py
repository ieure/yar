# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

"""Data I/O serial interface."""

import serial
import array
import time
from . import format
from yar.cksum import *

EOL = "\r"

ERRS = ((2**31, "Error:"),
        (2**26, "Serial overrun error"),
        (2**25, "Serial framing error"),
        (2**24, "Buffer overflow error"),
        (2**23, "Programming error"),
        (2**22, "Start line not set high"),
        (2**21, "L2 + L3 > DEVICE"),
        (2**20, "Composite DAC error"),
        (2**19, "Device not blank"),
        (2**18, "Illegal bit"),
        (2**17, "Verification failed"),
        (2**16, "Incomplete programming, or no card set"),
        (2**15, "I/O error"),
        (2**12, "Compare error"),
        (2**11, "Checksum error"),
        (2**10, "Record count, address check, or record type error"),
        (2**9, "Address error"),
        (2**8, "Data not hexidecimal, or insufficient data received"),
        (2**7, "RAM error"),
        (2**5, "L2 + L3 > RAM"),
        (2**4, "Invalid center point for split or shuffle"),
        (2**3, "Illegal split or shuffle"),
        (2**2, "No RAM or insufficient RAM"),
        (2**1, "RAM write error, or program memory failure"),
        (2**0, "RAM end not on 1K boundary"))


def decode_errors(err):
    """Return errors which err represents."""
    return " ".join([msg for (key, msg) in ERRS if err & key])


def errorp(err):
    """Is this code an error?"""
    return bool(err & 2**31)


class Yar():

    """Class for communicating with Data I/O devices."""

    def __init__(self, *args, **kwargs):
        kwargs['timeout'] = 0
        self.port = serial.Serial(*args, **kwargs)

    def _writeline(self, line, *args):
        """Write a line to the programmer."""
        self.port.write((line + EOL) % args)

    def _readline(self):
        """Read a line from the programmer. Returns None or line.

           The device may be slow to produce a response, so we try a
           few times with a delay in between."""
        tries = 1
        if self.port.inWaiting() == 0 and tries <= 3:
            time.sleep(tries * .25)
            tries += 1

        if self.port.inWaiting() == 0:
            return None

        buf = ""
        ch = ""
        while ch != EOL:
            ch = self.port.read(1)
            buf += ch

        return buf.strip()

    def _readok(self):
        """Await a response, returning a boolean indicating success."""
        line = self._readline()
        if line == None:
            return None
        elif line[-1] == "?" or line[-1] == ">":
            return line[:-1] or True
        return False

    def _await(self, max=60):
        """Await a response for long-running operations.
           Does not read the response.

           This will wait up to max seconds for a response.
           Returns True if a response is waiting, False if timed out."""
        tries = 0
        while self.port.inWaiting() == 0 and tries < max:
            time.sleep(1)
            tries += 1
        return tries != max

    def last_error(self):
        """Return the last error, or None"""
        self._writeline("F")
        resp = self._readok()
        return resp and decode_errors(int(resp, 16)) or None

    def ping(self):
        """Ping the programmer. Returns True if it is responding."""
        self._writeline("H")
        return self._readok()

    def _resp(self):
        """Return the response, or raise an exception."""
        r = self._readok()
        if not r:
            raise Exception(self.last_error())
        return r

    def config(self):
        """Return device configuration."""
        self._writeline("G")
        return self._readok()

    def blank_test(self):
        """Ensure the device in the programmer is blank."""
        self._writeline("B")
        self._await()
        return self._readok()

    def illegal_bit_test(self):
        self._writeline("T")
        self._readok()

    def select(self, function):
        """Select an extended function."""
        self._writeline("%02x]" % function)
        return self._readok()

    def set_block_size(self, size):
        self._writeline("%04x;", size)
        return self._readok()

    def set_record_size(self, size):
        self._writeline("%02xH", size)
        return self._readok()

    def set_format(self, format, control_code=0):
        """Set the format used to send and receive data."""
        self._writeline("%x%02xA" % (control_code, format))
        return self._readok()

    def set_device(self, family, pinout):
        """Set the device type to use."""
        self._writeline("%x%x@", family, pinout)
        self._resp()

    def get_device(self):
        """Return the currently selected family and pinout."""
        self._writeline("[")
        resp = self._resp()
        return (int(resp[0:2], 16), int(resp[2:4], 16))

    def load(self):
        """Load a device's contents and return the checksum."""
        self._writeline("L")
        self._await()
        return self._readok()

    def checksum(self):
        """Return the checksum of programmer RAM"""
        self._writeline("S")
        self._await()
        r = self._readok()
        return r and int(r, 16) or r

    def flush(self):
        """Flush any data waiting in the read buffer."""
        if self.port.inWaiting() > 0:
            self.port.read(self.port.inWaiting())

    def clear_ram(self):
        """Zero out device memory."""
        self._writeline("^")
        self._await()
        return self._readok()

    def program_device(self):
        """Write programmer RAM to device."""
        self._writeline("P")
        self._await(max=300)
        return self._readok()

    def verify(self):
        """Verify a device against programmer RAM."""
        self._writeline("V")
        self._await(max=300)
        return self._readok()

    def dump_to(self, outp):
        """Dump programmer RAM to file-like object."""
        yar.set_format(format.BINARY)
        self._writeline("O")
        done = False
        tries = 1
        while not done:
            if tries > 15:
                return True

            if self.port.inWaiting() == 0:
                # Wait for data
                tries += 1
                time.sleep(tries*.2)
                continue

            outp.write(self.port.read(self.port.inWaiting()))
            tries = 1

    def load_from(self, inp):
        """Load programmer RAM from file-like object."""
        bytes = file_to_bytes(inp)
        sum = checksum(bytes) & 0xFFFF
        self.set_format(format.BINARY)
        self._writeline("I")

        # Header
        header = [0x08, 0x1C, 0x2A, 0x49, 0x08]
        self.port.write(header)

        # Null
        self.port.write([0x00])

        # Data length
        # FIXME this is stupid but I can't think right now.
        self.port.write([int(n, 16) for n in '%04x' % len(bytes)])

        self.port.write([127])  # Rubout

        # Data
        self.port.write(bytes)

        # Trailer
        self.port.write([0x00, 0x00])

        # Checksum
        self.port.write([sum >> 8, sum & 0xFF])

        self._await()
        if not self._readok():
            raise Exception(self.last_error())
        s = self.checksum()
        if s != sum:
            raise Exception("Checksum error!")
