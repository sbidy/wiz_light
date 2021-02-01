"""WiZ Light integration."""
import logging
from math import atan2, cos, pi
from operator import epsilon

from pywizlight.bulb import PilotBuilder

from .vec import MathHelper

_LOGGER = logging.getLogger(__name__)


class ColorHelper:
    """Manages the RGBCW color."""

    angle = (pi * 2) / 3
    basis = (
        MathHelper.vecFromAngle(0),
        MathHelper.vecFromAngle(angle),
        MathHelper.vecFromAngle(angle * 2),
    )
    # the max value we will use for c and w
    cwMax = 128
    buffer = ""

    @classmethod
    def debug(cls, msg, end="\n"):
        cls.buffer += msg
        if end == "\n":
            _LOGGER.debug(cls.buffer)
            cls.buffer = ""
        else:
            cls.buffer += end

    @classmethod
    def printBasis(cls, basis, prefix=""):
        cls.debug("{}Basis Vectors: ".format(prefix), end="")
        for vector in basis:
            cls.debug("{} ".format(MathHelper.vecFormat(vector)), end="")
        cls.debug("")

    @classmethod
    def trapezoid(cls, hueVec, saturation, brightness):
        """This function computes the linear combination of two basis vectors that define a trapezoid.

        hueVec - a normalized vector in the hue color wheel (0..1, 0..1, 0..1)
        saturation - a single value representing the length of the hue vector (0..1)
        brightness - a separate value that may be passed in, and should be used in the Pilot.
        """

        # if saturation is essentially 0, just go to the full on
        if saturation <= epsilon:
            rgb = (0, 0, 0)
        else:
            # we want to compute the actual RGB color of the saturated point as a linear
            # combination of no more than two of the basis vectors. first we have to figure
            # out which of the basis vectors we will use
            maxAngle = cos((pi * 2 / 3) - epsilon)
            mask = tuple(
                [
                    (1 if (MathHelper.vecDot(hueVec, vector) > maxAngle) else 0)
                    for vector in cls.basis
                ]
            )
            count = sum(mask)
            cls.debug(
                "    Max Angle: {:0.3f}, Mask: ({}, {}, {}), Count: {}".format(
                    maxAngle, mask[0], mask[1], mask[2], count
                )
            )
            if count == 1:
                # easy case, it's just one color component
                rgb = mask
            else:
                # recast as a ray-line intersection using the two found basis vectors, note
                # the basis vectors are normalized by definition
                subBasis = [
                    cls.basis[i] for i, maskVal in enumerate(mask) if (maskVal == 1)
                ]
                cls.printBasis(subBasis, "    ")

                # define the line from the origin along the second vector, computing its
                # equation in the form Ax + C = 0, but C is always 0 for this line
                AB = (subBasis[1][1], subBasis[1][0] * -1)

                # intersect the ray from the saturation point along the first basis vector
                # with the line we just computed, these are definitely not co-linear, so there
                # should always be an intersection point, and the result should always be in
                # the range [-1 .. 1], this is the first basis coefficient
                coeff = [0, 0]
                coeff[0] = MathHelper.vecDot(hueVec, AB) / MathHelper.vecDot(
                    subBasis[0], AB
                )

                # compute the intersection point, and the second basis coefficient, note that
                # we compute the coefficients to always be positive, but the intersection calculation
                # needs to be in the opposite direction from the basis vector (hence the negative on
                # coeff[0]).
                intersection = MathHelper.vecAdd(
                    MathHelper.vecMul(subBasis[0], -coeff[0]), hueVec
                )
                coeff[1] = MathHelper.vecDot(intersection, subBasis[1])

                cls.debug(
                    "    Intersection Point: {}, Coefficients: {}".format(
                        MathHelper.vecFormat(intersection), MathHelper.vecFormat(coeff)
                    )
                )

                # there's a bit of a gamut problem here, as the area outside the hexagon defined by
                # the three unit basis vectors is not actually reachable. this manifests as
                # coefficients greater than 1, which will always happen unless the target color is
                # either one of the basis vectors or a bisector of two basis vectors. we scale both
                # coefficients by 1/maxCoefficient to make valid colors
                maxCoeff = max(coeff[0], coeff[1])
                coeff = [c / maxCoeff for c in coeff]
                cls.debug(
                    "    Scaled Coefficients: {}".format(MathHelper.vecFormat(coeff))
                )

                # now rebuild the rgb vector by putting the coefficients into the correct place
                j = 0
                rgbList = []
                for i in range(3):
                    if mask[i] == 1:
                        rgbList.append(min(coeff[j], 1))
                        j += 1
                    else:
                        rgbList.append(0)
                rgb = tuple(rgbList)

        # we want a discontinuous behavior. if saturation >= 0.5, we want the color to remain saturated
        # and we scale the cw value down to 0 as saturation goes from 0.5 to 1. if saturation < 0.5, we
        # want to saturate cw, and scale the rgb down to (0, 0, 0) as saturation goes from 0.5 - 0
        if saturation >= 0.5:
            # rgb remains saturated
            # scale the cw value down to 0 as saturation goes from 0.5 to 1
            cw = 1 - ((saturation - 0.5) * 2)
        else:
            cw = 1
            rgb = MathHelper.vecMul(rgb, saturation * 2)

        # scale back to the pilot color space
        rgb = MathHelper.vecInt(MathHelper.vecMul(rgb, 255))
        cw = int(max(0, cw * cls.cwMax))
        if cw == 0:
            cw = None

        cls.debug("    RGB OUT: {}, CW: {}".format(rgb, cw))

        # the wiz light appears to have 5 different LEDs, r, g, b, warm_white, and cold_white
        # there appears to be a max power supplied across the 5 LEDs, which explains why all-
        # on full isn't the brightest configuration
        # warm_white appears to be 2800k, and cold_white appears to be 6200k, somewhat neutral
        # brightness is achieved by turning both of them on
        return PilotBuilder(
            rgb=rgb, warm_white=cw, cold_white=cw, brightness=brightness
        )

    @classmethod
    def rgb2rgbcw(cls, rgb, brightness) -> trapezoid:
        """Convert rgb to rgbcw.

        Given a rgb tuple in the range (0..255, 0..255, 0-255), convert that to a rgbcw for the wiz
        light. brightness may or may not be passed in and is passed through to the trapezoid function.
        """
        cls.debug("RGB IN: {}, BRIGHTNESS: {}".format(rgb, brightness))

        # scale the vector into canonical space ([0-1])
        rgb = MathHelper.vecMul(rgb, 1 / 255)

        # compute the hue vector as a linear combination of the basis vectors, and extract the
        # saturation, there's probably a better pythonese way of doing this
        hueVec = MathHelper.vecAdd(
            MathHelper.vecAdd(
                MathHelper.vecMul(cls.basis[0], rgb[0]),
                MathHelper.vecMul(cls.basis[1], rgb[1]),
            ),
            MathHelper.vecMul(cls.basis[2], rgb[2]),
        )
        saturation = MathHelper.vecLen(hueVec)
        if saturation > epsilon:
            hueVec = MathHelper.vecMul(hueVec, 1 / saturation)

        return cls.trapezoid(hueVec, saturation, brightness)

    @classmethod
    def rgbcw2hs(cls, rgb, cw):
        """Convert rgb hue.

        Given a tuple that is r,g,b and cw in 0-255 range, convert that to a hue, saturation tuple in the
        range (0..360, 0..100).
        """

        # scale the rgb and cw values into canonical space (the wiz app might set cw to higher than the
        # value we use, so we have to allow for that
        rgb = MathHelper.vecMul(rgb, 1 / 255)
        cw = min(cw, cls.cwMax) / cls.cwMax

        # compute the hue vector as a linear combination of the basis vectors, there's probably a
        # better pythonese way of doing this
        hueVec = MathHelper.vecAdd(
            MathHelper.vecAdd(
                MathHelper.vecMul(cls.basis[0], rgb[0]),
                MathHelper.vecMul(cls.basis[1], rgb[1]),
            ),
            MathHelper.vecMul(cls.basis[2], rgb[2]),
        )
        cls.debug(
            "RGB IN: {}, CW: {:.3f}, HUE VECTOR: {}".format(
                MathHelper.vecFormat(rgb), cw, MathHelper.vecFormat(hueVec)
            )
        )

        # the discontinuous nature of the wiz bulb setting means we have two different states:
        # 1) the cw value is 1, and the hue vector is scaled (from 50% saturation to white)
        # 2) the hue vector is saturated, and cw is scaled down (from 50% saturation to full color)
        if cw == 1:
            # hue scales down to (0, 0) at saturation 0, up to unit length at 50% saturation, so we get
            # that length, normalize the vector, and scale the saturation to reflect the half range
            hueVecLength = MathHelper.vecLen(hueVec)
            if hueVecLength > epsilon:
                MathHelper.vecMul(hueVec, 1 / hueVecLength)
            saturation = hueVecLength * 0.5
        else:
            # the hue vector is already fully saturated, and cw scales from 0 - 0.5 to add in white light
            saturation = 1 - (cw / 2)

        # we have a saturated version of the hue vector now, which we convert to a hue vector and
        # then extract the angle of the vector in radians. We add 2 Pi to the angle if it is less than
        # 0 to put the hue angle in the range from 0 to 2 Pi
        hue = atan2(hueVec[1], hueVec[0])
        while hue < 0:
            hue += pi * 2

        # scale the hue/saturation values back to their native ranges and return the tuple
        hue *= 180 / pi
        saturation *= 100
        cls.debug("    HUE OUT: {:.5f}, SATURATION: {:.3f}".format(hue, saturation))
        return hue, saturation

    @classmethod
    def hs2rgbcw(cls, hs, brightness):
        """Convert hue to a canonical value.

        given a hue, saturation tuple in the range (0..360, 0..100), convert that to a rgbcw for the wiz light
        brightness may or may not be passed in and is passed through to the trapezoid function.
        """
        hueCanonical = hs[0] / 360
        while hueCanonical >= 1:
            hueCanonical -= 1

        # compute hue in a discretized space and convert to radians, then a vector
        hueRadians = hueCanonical * pi * 2
        hueVec = MathHelper.vecFromAngle(hueRadians)

        # convert saturation to a canonical value in a discretized space
        # we take the square root to give the user more visual control
        saturation = hs[1] / 100

        cls.debug(
            "HS IN: {}, HUE: {:.5f}, SATURATION: {:.3f}, BRIGHTNESS: {}".format(
                MathHelper.vecFormat(hs), hueRadians, saturation, brightness
            )
        )

        return cls.trapezoid(hueVec, saturation, brightness)