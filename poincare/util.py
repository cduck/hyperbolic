
import math


def radialEuclidToPoincare(r):
    return 2 * math.atanh(r)
def radialPoincareToEuclid(r):
    return math.tanh(r/2)

