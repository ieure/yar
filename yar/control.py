# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

"""Data I/O serial interface."""

import array
import logging
import serial
import sys
import time
from . import format
from yar.cksum import *
import yar.io as io

EOL = "\r"

 # Error handling

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


class ProgrammerError(IOError):

    def __init__(self, code):
        IOError.__init__(self, decode_errors(code))

    def __unicode__(self):
        return self.message


def decode_errors(err):
    """Return errors which err represents."""
    return " ".join([msg for (key, msg) in ERRS if err & key])


def errorp(err):
    """Is this code an error?"""
    return bool(err & 2**31)


class Yar():

    """Class for communicating with Data I/O devices."""

    _log = logging.getLogger("Yar")

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

    def _resp(self):
        """Return the response, or raise an exception."""
        r = self._readok()
        if r == None:
            return r
        if not r:
            err = self.last_error()
            if not err:
                raise IOError("Failed to get error status!")
            raise ProgrammerError(err)
        return r

    def _await(self, max=60, fd=None):
        """Await a response for long-running operations.
           Does not read the response.

           This will wait up to max seconds for a response.
           Returns True if a response is waiting, False if timed out."""
        tries = 0
        while self.port.inWaiting() == 0 and tries < max:
            time.sleep(1)
            tries += 1
        if tries == max:
            raise IOError("Timed out after %ds" % max)
        return tries != max

    def last_error(self):
        """Return the last error, or None"""
        self._writeline("F")
        resp = self._readok()
        return resp and errorp(int(resp, 16)) or None

    def ping(self):
        """Ping the programmer. Returns True if it is responding."""
        self._log.debug("ping()")
        self._writeline("H")
        res = self._readok()
        if res:
            self._log.debug("ping(): pong")
        else:
            self._log.debug("ping(): No response")
        return res

    def abort(self):
        self.port.write([0x27])
        self.flush()

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

    def await_start(self):
        """Wait for the operator to press START on the programmer."""
        self._writeline('%%')
        r = self._await(6000)
        if not r:
            return r
        return self._readok()

    def set_format(self, format, control_code=0):
        """Set the format used to send and receive data."""
        self._writeline("%x%02xA" % (control_code, format))
        return self._readok()

    def set_device(self, family, pinout):
        """Set the device type to use."""
        self._writeline("%x%x@", family & 0xFF, pinout & 0xFF)
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
        r = self._resp()
        return r and int(r, 16) or r

    def flush(self):
        """Flush any data waiting in the read buffer."""
        if self.port.inWaiting() > 0:
            self.port.flushInput()

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

    def dump_to(self, outp, progress_to=None):
        """Dump programmer RAM to file-like object."""
        out = progress_to or sys.stderr
        self.set_format(format.BINARY)
        self._writeline("O")
        data_buf = array.array("B")
        header = array.array("B")

        # Read 16-byte header
        while len(header) < 16:
            header.fromstring(self.port.read(1))

        if header[:10].tolist() != [0x0D, 0x08, 0x1C, 0x3E, 0x6B, 0x08,
                                    0x00, 0x00, 0x00, 0x00]:
            msg = "Invalid header " + " ".join([r"%02x"] * len(header))
            raise IOError(msg % tuple(header.tolist()))

        sz = int("".join(map(str, header[0x0A:0x0F])), 16)
        p = io.Progress(sz)
        while len(data_buf) < sz:
            # Don't overflow the buffer
            tr = self.port.read(min(sz - len(data_buf), 128))
            if tr != '':
                data_buf.fromstring(tr)
                p.update(len(data_buf))
                out.write(repr(p) + "\r")
                out.flush()
            else:
                time.sleep(.1)

        # Two nulls + checksum
        trailer = array.array("B")
        while len(trailer) < 4:
            trailer.fromstring(self.port.read(1))

        prog_sum = (trailer[2] << 8) + trailer[3]
        pload_sum = checksum(data_buf) & 0xFFFF
        if prog_sum != pload_sum:
            raise IOError("Programmer cksum %04x != data cksum %04x" % (
                prog_sum, pload_sum))
        data_buf.tofile(outp)

    def load_from(self, inp, progress_to=None):
        """Load programmer RAM from file-like object."""
        out = progress_to or sys.stderr
        bytes = io.file_to_bytes(inp)
        p = io.Progress(len(bytes))
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

        self.port.write([0xFF])  # Rubout

        # Data
        sent = 0
        while len(bytes) > 0:
            block = min(128, len(bytes))
            assert block > 0, "Can't send empty block"
            loop_bytes = bytes[:block]
            written = self.port.write(loop_bytes)
            assert written == block, "Incomplete write"
            assert self.port.inWaiting() == 0, \
                "Programmer is trying to tell us something"
            self.port.flush()
            sent += written
            p.update(sent)
            out.write(repr(p) + "\r")
            out.flush()
            bytes = bytes[block:]  # Truncate buffer
            time.sleep(.1)

        out.write("\n")
        out.flush()

        # Trailer
        self.port.write([0x00, 0x00])

        # Checksum
        self.port.write([sum >> 8, sum & 0xFF])

        self._await()
        self._resp()
        s = self.checksum()
        if s != sum:
            raise IOError(
                "Checksum error! Input checksum %06x != reported %06x" % (
                    sum, s))
