# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure.
# Author: Ian Eure <ian.eure@gmail.com>
#

"""Yar CLI."""

import serial
import sys
from newcontrol import Yar
import format
import cksum
from optparse import OptionParser, OptionGroup

def summarize(f):
    """Return the function's doc summary."""
    return (f.__doc__ or "").split("\n", 1)[0].strip()


def get_commands():
    return sorted(
        (name[:-4], summarize(f), f)
        for (name, f) in globals().iteritems() if name.endswith("_cmd"))


def get_parser():
    usage = "Usage: %prog [OPTIONS] COMMAND [ARG ARG ...]\n\nCommands:\n\n"

    for (name, doc, _) in get_commands():
        usage += "  %s - %s\n" % (name, doc)

    p = OptionParser(usage[:-1])

    cg = OptionGroup(p, "Connection options")

    cg.add_option("--port", "-p", default="/dev/cu.usbserial",
                  help="Serial port programmer is connected to")
    cg.add_option("--baud", "-b", default=9600,
                  help="Communication speed. Default: 9600.")
    cg.add_option("--parity", default="N81", help="Connection parity/data/stop. Default: N81")
    p.add_option_group(cg)

    p.add_option("--pak", help="Pak instaled in the programmer: uni, uni2, uni2b, logic, gang")

    p.add_option("--device", help="Device ID; looks up family/pinout")

    p.add_option("--family", help="Device family")
    p.add_option("--pinout", help="Device pinout")
    p.add_option("--detect", help="Autodetect device (on some Paks)")

    return p


def connect(yar):
    """Ensure that the programmer is connected."""
    yar.flush()
    c = yar.ping()
    if c:
        return

    sys.stdout.write("Put device in remote mode: SELECT F1 START START")
    while not yar.ping():
        pass
    print " connected."


def configure(yar, opts):
    """Configure the programmer for the given options"""
    connect()
    if opts.detect:
        yar.select(0xBD)
        yar.set_device(0xFF, 0xFF)

    if opts.family and opts.pinout:
        yar.set_device(int(opts.family, 16),
                       int(opts.pinout, 16))


def checksum_cmd(yar, *args):
    """Checksum files"""
    for file_ in args:
        with open(file_, 'rb') as fp:
            print "%s - %06x" % (
                file_, cksum.checksum(cksum.file_to_bytes(fp)))
    return 0


def dumpram_cmd(yar, output):
    """Dump programmer RAM to file."""
    yar.flush()
    if not yar.ping():
        print yar.last_error()
        return 1

    print "Dumping"
    with open(output, 'wb') as fp:
        yar.dump_to(fp)

    return 0


def loaddev_cmd(yar):
    """Load device contents into programmer RAM"""
    yar.clear_ram()
    yar.load()
    return 0


def loadfile_cmd(yar, file_):
    """Load file contents into programmer RAM"""
    connect(yar)
    yar.clear_ram()
    with open(file_, "rb") as inp:
        yar.load_from(inp)


def main():
    """Yar main entry point"""
    p = get_parser()
    (opts, cmd_args) = p.parse_args()
    (cmd, args) = (cmd_args[0], cmd_args[1:])
    c = Yar(opts.port)           # FIXME, use all settings
    sys.exit(CMDS[cmd](c, *args))
