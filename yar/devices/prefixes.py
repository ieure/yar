# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

"""Manufacturer prefixes."""

from collections import defaultdict

# Map of device manufacturer abbrev to parts prefix
_PREFIXES = {
    'AMD': ('a', 'am', 'ampal', 'mach', 'pal', 'palce'),
    'ASA': (),                  # FIXME
    'ATM': ('at', 'atv'),
    'CAT': (),                  # n/a
    'CYP': ('cy', 'palce'),
    'EAI': (),                  # n/a
    'EXL': (),                  # n/a
    # Fairchild
    'FAR': ('a', 'dm', 'f', 'l', 'mm', 'nm', 'nmc', 'unx'),
    # Fujitsu
    'FUJ': ('mb', 'mbl8', 'mbm'),
    # GoldStar
    'GSC': ('gl', 'gm', 'gmm'),
    # Harris
    'HAR': ('ad', 'ca', 'cd', 'cdp', 'cp', 'cs', 'dg', 'h', 'ha',
            'hfa', 'hi', 'hin', 'hip', 'hv', 'ich', 'icl', 'icm',
            'im'),
    # Hitachi
    'HIT': ('ha', 'hd', 'hg', 'hl', 'hm', 'hn'),
    # Hughes
    'HUG': (),                  # n/a
    # Hyundai
    'HYU': ('hy',),
    # International CMOS Technology
    'ICT': (),                  # n/a
    # Integrated Device Technology
    'IDT': ('idt',),
    # Intel
    'INT': ('c', 'd', 'i', 'n', 'p', 'pa'),
    # Intersil
    'ISL': (),                  # n/a
    # Lattice Semiconductor
    'LAT': ('gal', 'isplsi'),
    # Microchip Technology Inc./GI
    'MCT': ('acf', 'gic', 'gp', 'spr'),
    # Mostek?
    'MIK': (), # FIXME
    # Mitsubishi
    'MIT': ('m', 'msl8'),
    # MOS Technology
    'MOS': (), # FIXME
    # Motorola
    'MOT': ('hep', 'lf', 'mc', 'mcc', 'mccs', 'mcm', 'mct', 'mec', 'mm', 'mpf', 'mpq', 'mps', 'mpsa', 'mwm', 'sg', 'sn', 'tda', 'tl', 'ua', 'uc', 'uln', 'xc'),
    # National Semiconductor
    'NAT': ('a', 'adc', 'clc', 'cop', 'dac', 'dm', 'dp', 'ds', 'f', 'l', 'lf', 'lft', 'lh', 'lm', 'lmc', 'lmd', 'lmf', 'lmx', 'lpc', 'mf', 'mm', 'nh', 'unx'),
    'NEC': ('pb', 'pc', 'pd', 'upd', 'upd8'),
    'OKI': ('msc', 'msm'),
    'OWS': (), # FIXME
    'PAN': (), # FIXME
    'PHL': (), # FIXME
    # Raytheon
    'RAY': ('r', 'ray', 'rc', 'rm'),
    # Ricoh
    'RIC': (),                  # n/a
    # Rockwell International
    'ROC': ('r',),
    # Samsung
    'SAM': ('ka', 'km', 'kmm'),
    # SEEQ Technology
    'SEQ': ('nq', 'pq'),
    # SGS-Thomson Microelectronics
    'SGS': (),                  # n/a
    # Sharp
    'SHP': ('ir',),
    # S-Mos Sytems
    'SMS': (),                  # n/a
    # ???
    'SON': (),
    # Texas Instruments
    'TEX': ('mc', 'ne', 'op', 'rc', 'sg', 'sn', 'tpbpal', 'til', 'tip', 'tipal', 'tis', 'tl', 'tlc', 'tle', 'tm', 'tms', 'ua', 'uln'),
    # Toshiba
    'TOS': ('t', 'ta', 'tc', 'td', 'thm', 'tmm', 'tmp', 'tmpz'),
    # VLSI
    'VTI': ('vt',),
    # Waferscale Integration
    'WSI': ('psd',),
    # XICOR
    'XIC': ('x',),
    # XILINX
    'XIL': ()                   # n/a
}

class Prefixes():

    prefs = None
    inverted = None

    def __init__(self):
        self.prefs = _PREFIXES
        self.inverted = self.invert(_PREFIXES)

    def get_mfgrs(self, prefix):
        """Return possible manufacturers for this prefix."""
        return self.inverted.get(prefix) or set()

    def get_prefixes(self, mfgr):
        """Return possible prefixes for this manufacturer."""
        return self.prefs.get(mfgr) or set()

    def re(self, prefixes=None):
        """Return a regex matching prefixes."""
        prefixes = prefixes or reduce(lambda a, b: set(a).union(set(b)),
                                      self.prefs.values())
        return "(%s)" % "|".join(prefixes)

    def invert(self, prefixes):
        """Return an inverted index of prefixes."""
        d = defaultdict(set)
        for (m, pfxs) in prefixes.iteritems():
            ms = set([m])
            for pfx in pfxs:
                d[pfx].update(ms)
        return d

prefixes = Prefixes()
