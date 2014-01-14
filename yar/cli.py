# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure.
# Author: Ian Eure <ian.eure@gmail.com>
#

"""Yar CLI."""

from itertools import chain
from optparse import OptionParser, OptionGroup
from os.path import basename
import format
import re
import sys

import serial

from control import Yar
from devices.matcher import match
import yar.pak as pak
import yar.cksum as cksum
import yar.io as io


def summarize(f):
    """Return the function's doc summary."""
    return (f.__doc__ or "").split("\n", 1)[0].strip()


def get_commands():
    return sorted(
        (name[:-4], summarize(f), f)
        for (name, f) in globals().iteritems() if name.endswith("_cmd"))


def get_commands_map():
    return dict((name, f) for (name, _, f) in get_commands())


def expand_command(cmd, cmds):
    """Match a command, returning the name of the full, unambiguous cmd."""
    cmd_re = re.compile("^" + ".*".join(cmd) + ".*", re.I)
    cs = [name for name in cmds if cmd_re.match(name)]
    if len(cs) == 1:
        return cs[0]
    return None


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

    dg = OptionGroup(p, "Device options")
    dg.add_option("--pak", help="Pak instaled in the programmer: unipak, unipak2, unipak2b, logicpak, gangpak")

    dg.add_option("--device", help="Device ID; looks up family/pinout")

    dg.add_option("--family", help="Device family")
    dg.add_option("--pinout", help="Device pinout")
    dg.add_option("--detect", help="Autodetect device (on some Paks)",
                  action="store_true")
    p.add_option_group(dg)

    return p


def await_operator(yar, msg):
    sys.stdout.write(msg or "Press START...")
    sys.stdout.flush()
    r = yar.await_start()
    if not r:
        raise Exception("Timed out")
    print "ok."
    return r


 # Commands


def checksum_cmd(_, *args):
    """Checksum files"""
    for (inpf, fd) in chain.from_iterable(io.gen_fds(args)):
        print "%s %06x" % (
            basename(inpf), cksum.checksum(io.file_to_bytes(fd)))
    return 0


def dumpram_cmd(s, output):
    """Dump programmer RAM to file."""
    yar = s.yar()
    s.yar().flush()
    if not yar.ping():
        print yar.last_error()
        return 1

    with open(output, 'wb') as fp:
        yar.dump_to(fp)

    return 0


def loaddev_cmd(s):
    """Load device contents into programmer RAM"""
    yar = s.yar()
    yar.clear_ram()
    await_operator(
        yar, "Insert device into indicated socket, then press START...")
    sum = yar.load()
    print "Checksum: %06x" % sum
    return 0


def loadfile_cmd(yar, file_):
    """Load file contents into programmer RAM"""
    connect(yar)
    yar.clear_ram()
    with open(file_, "rb") as inp:
        yar.load_from(inp)


def lookup_cmd(s, device):
    """Look up a device family/pinout"""
    try:
        (family, pinout) = match(s.pak().DEVICES, device)
        print "%s family %03x pinout %03x" % (device, family, pinout)
        return 0
    except ValueError, e:
        print e
        return 1


 # Main code

class GlobalState():

    _yar = None
    opts = None
    args = None

    def __init__(self, opts, args):
        self.opts = opts
        self.args = args

    def yar(self):
        """Return a configured Yar instance."""
        if not self._yar:
            self._yar = self._construct()
            self._connect(self._yar)
            self._configure(self._yar)
        return self._yar

    def pak(self):
        """Return the configured Pak."""
        return pak.load(self.opts.pak)

    def _construct(self):
        return Yar(self.opts.port)           # FIXME, use all settings

    def _connect(self, yar):
        """Ensure that the programmer is connected."""
        yar.flush()
        c = yar.ping()
        if c:
            return

            sys.stdout.write("Put device in remote mode: SELECT F1 START START")
            while not yar.ping():
                pass
                print " connected."

    def _configure(self, yar):
        """Configure the programmer for the given options"""
        if self.opts.detect:
            yar.select(0xBD)
            yar.set_device(0xFF, 0xFF)

        if self.opts.device:
            (family, pinout) = match(self.pak().DEVICES, self.opts.device)
            yar.set_device(family, pinout)

        if self.opts.family and self.opts.pinout:
                yar.set_device(int(self.opts.family, 16),
                               int(self.opts.pinout, 16))

def main():
    """Yar main entry point"""
    p = get_parser()
    (opts, cmd_args) = p.parse_args()
    if not cmd_args:
        p.print_help()
        sys.exit(-1)
    (cmd, args) = (cmd_args[0], cmd_args[1:])
    cmds = get_commands_map()
    cmd_ = expand_command(cmd, cmds.keys())
    cmd = cmd_ or cmd
    if cmd not in cmds:
        print "No such command: `%s'" % cmd
        p.print_help()
        sys.exit(-1)

    s = GlobalState(opts, args)

    # try:
    sys.exit(cmds[cmd](s, *args))
    # except Exception, e:
    #     print "%s" % e
    #     sys.exit(-2)
