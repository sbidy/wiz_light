"""WiZ Light integration."""

import logging
import math
import operator

# a small value, really close to zero, more than adequate for our 3 orders of magnitude
# of color resolution
epsilon = 1.0e-5

# a bunch of utility functions, just so we don't have to bring in any external dependencies
def vecDot (a, b):
    return sum(map(operator.mul, a, b))

def vecLenSq (a):
    return vecDot (a, a)

def vecLen (a):
    lenSq = vecLenSq (a)
    return math.sqrt (lenSq) if (lenSq > epsilon) else 0

def vecAdd (a, b):
    return tuple(map (operator.add, a, b))

def vecSub (a, b):
    return tuple(map (operator.sub, a, b))

def vecMul (vec, sca):
    return tuple([c * sca for c in vec])

def vecInt (vec):
    return tuple([int (c) for c in vec])

def vecNormalize (vec):
    len = vecLen (vec)
    return vecMul (vec, 1 / len) if (len > epsilon) else vec

def vecFormat (vec):
    return "({})".format (str([float ("{0:.3f}".format(n)) for n in vec])[1:-1])

def vecFromAngle (angle):
    return (math.cos (angle), math.sin (angle))
