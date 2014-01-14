# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

"""Match device names"""

import re
from . prefixes import prefixes

INPUT_RE = re.compile("^" + prefixes.re() + "?" + "([0-9a-z]+)$", re.I)

WHITESPACE_RE = re.compile("\s")

class AmbiguousDeviceError(ValueError):

    devices = []

    def __init__(self, input, devs):
        self.devices = devs
        ValueError.__init__(
            self, "Ambiguous device `%s', matches: %s" % (
                input, ", ".join(devs)))


class NoMatchingDeviceError(ValueError):

    device = None

    def __init__(self, input):
        self.device = input
        ValueError.__init__(self, "No matching device for `%s'" % input)


def extract(input):
    """Return the manufacturer, part, and packaging from a device ID."""
    return INPUT_RE.match(re.sub(r'\s+', '', input))


def distance(s1, s2):
    """Return the Levenshtein distance between strings a and b."""
    if len(s1) < len(s2):
        return distance(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = xrange(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def matches(devices, device):
    cpts = extract(device.lower())
    if not cpts:
        raise ValueError("Unknown part format")
    c = cpts.groups()
    (mfgr, part) = c

    return (c, [ent for ent in devices if ent[1].lower() == part])


def narrow_by_manuf(mpref, candidates):
    m = prefixes.get_mfgrs(mpref)
    if not m:
        return candidates

    return [c for c in candidates if c[0] in m]


def match(devices, device):
    """Match a device against a device list.

       The
    """
    ((mfgr, part), candidates) = matches(devices, device)
    # If everything comes back as the same pinout, use that.
    candidate_pinouts = set([ent[4:6] for ent in candidates])
    if len(candidate_pinouts) == 1:
        return list(candidate_pinouts)[0]

    # Find a matching manufacturer
    candidates = narrow_by_manuf(mfgr, candidates)
    candidate_pinouts = set([ent[4:6] for ent in candidates])
    # Eliminated the dupes, we're good
    if len(candidate_pinouts) == 1:
        return list(candidate_pinouts)[0]

    # Nothing matched
    if not candidates:
        raise NoMatchingDeviceError(device)
        raise ValueError()

    # Ambiguous match
    possible = ["%s %s" % ent[0:2] for ent in candidates]
    raise AmbiguousDeviceError(device, possible)


def similarity(prefix, part, device):
    (mfgr, dpart, _, _, _, _) = device
    # Who manufactured parts with this prefix?
    mfgrs = prefixes.get_mfgrs(prefix)

    # 50% - this manufacturer could have made the part
    w = 0 if mfgr in mfgrs else 50
    d = distance(part, dpart)
    # print "`%s'->`%s' distance=%d" % (part, dpart, d)
    return 100 - w - d * 10


def similar(devices, device):
    cpts = extract(device.lower())
    if not cpts:
        raise ValueError("Unknown part format")
    c = cpts.groups()
    (pref, part) = c

    # Manuf?
    mfgrs = prefixes.get_mfgrs(pref)

    return sorted(devices, reverse=True,
                  key=lambda d: similarity(pref, part, d))[:10]
