
import math


def radialEuclidToPoincare(r):
    return 2 * math.atanh(r)
def radialPoincareToEuclid(r):
    return math.tanh(r/2)
def poincareToEuclidFactor(hr):
    return math.cosh(hr/2)**2 / 2

def triangleSideForAngles(adj1, adj2, opposite):
    ''' Uses the hyperbolic law of cosines, solved for the side length

        Input angles in radians '''
    A, B, C = adj1, adj2, opposite
    c = math.acosh((math.cos(C) + math.cos(A)*math.cos(B)) /
                   (math.sin(A)*math.sin(B)))
    return c

def triangleAngleOppositeSide(adj1, adj2, oppositeLen):
    ''' Uses the hyperbolic law of cosines, solved for the angle opposite the
        given side

        Input angles in radians '''
    c, A, B = oppositeLen, adj1, adj2
    C = math.acos(math.cosh(c)*math.sin(A)*math.sin(B) -
                  math.cos(A)*math.cos(B))
    return C
