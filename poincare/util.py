
import math


def radialEuclidToPoincare(r):
    return 2 * math.atanh(r)
def radialPoincareToEuclid(r):
    return math.tanh(r/2)
def poincareToEuclidFactor(hr):
    return math.cosh(hr/2)**2 / 2

