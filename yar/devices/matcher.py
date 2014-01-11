# -*- coding: utf-8 -*-
#
# © 2014 Ian Eure
# Author: Ian Eure <ian.eure@gmail.com>
#

"""Match device names"""

import re
from . prefixes import PREFIX_RE, PREFIXES, PREFIX_INV


INPUT_RE = re.compile("^" + PREFIX_RE + "?" + "([0-9a-z]+)$", re.I)

WHITESPACE_RE = re.compile("\s")

def extract(input):
    """Return the manufacturer, part, and packaging from a device ID."""
    return INPUT_RE.match(re.sub(r'\s+', '', input))


def distance(a, b):
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


def narrow_by_manuf(manuf, candidates):
    m = PREFIX_INV.get(manuf)
    if not m:
        return candidates

    return [c for c in candidates if c[0] in m]


def match(devices, device):
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
        raise ValueError("No matching device for `%s'" % device)

    # Ambiguous match
    possible = ["%s %s" % ent[0:2] for ent in candidates]
    raise ValueError("Ambiguous device `%s', matches: %s" % (
        device, ", ".join(possible)))
