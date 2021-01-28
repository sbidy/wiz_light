"""WiZ Light integration."""


class MathHelper:
    """Helper class with some math.

    <<<<<<< HEAD
        A bunch of utility functions, just so we don't have to bring in any external dependencies.
    """

    # a small value, really close to zero, more than adequate for our 3 orders of magnitude
    # of color resolution
    epsilon = 1.0e-5

    @staticmethod
    def vecDot(a, b):
        """Retrun sum."""
        return sum(map(mul, a, b))

    @classmethod
    def vecLenSq(cls, a):
        """Retrun Square."""
        return cls.vecDot(a, a)

    @classmethod
    def vecLen(cls, a) -> float:
        """Retrun Square length."""
        lenSq = cls.vecLenSq(a)
        return sqrt(lenSq) if (lenSq > cls.epsilon) else 0

    @staticmethod
    def vecAdd(a, b) -> tuple:
        """Retrun tuple object with add."""
        return tuple(map(add, a, b))

    @staticmethod
    def vecSub(a, b):
        """Retruns something."""
        return tuple(map(sub, a, b))

    @staticmethod
    def vecMul(vec, sca):
        """Retruns something."""
        return tuple([c * sca for c in vec])

    @staticmethod
    def vecInt(vec):
        """Retruns something."""
        return tuple([int(c) for c in vec])

    @classmethod
    def vecNormalize(cls, vec):
        """Retruns something."""
        len = cls.vecLen(vec)
        return cls.vecMul(vec, 1 / len) if (len > cls.epsilon) else vec

    @staticmethod
    def vecFormat(vec) -> str:
        """Retruns something."""
        return "({})".format(str([float("{0:.3f}".format(n)) for n in vec])[1:-1])

    @staticmethod
    def vecFromAngle(angle):
        """Retruns something."""
        return (cos(angle), sin(angle))
