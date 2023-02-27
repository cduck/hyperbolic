import math


def radial_euclid_to_poincare(r):
    return 2 * math.atanh(r)
def radial_poincare_to_euclid(r):
    return math.tanh(r/2)
def poincare_to_euclid_factor(hr):
    return math.cosh(hr/2)**2 / 2

def triangle_side_for_angles(adj1, adj2, opposite):
    '''Solve for a hyperbolic triangle side length from three angles.

    Uses the hyperbolic law of cosines to solve for the side length.  Input
    angles in radians.
    '''
    A, B, C = adj1, adj2, opposite
    c = math.acosh((math.cos(C) + math.cos(A)*math.cos(B)) /
                   (math.sin(A)*math.sin(B)))
    return c

def triangle_angle_opposite_side(adj1, adj2, opposite_len):
    '''Solve for a hyperbolic triangle angle from the other two angles and
    opposite side length.

    Uses the hyperbolic law of cosines to solve for the angle opposite the given
    side.  Input angles in radians.
    '''
    c, A, B = opposite_len, adj1, adj2
    C = math.acos(math.cosh(c)*math.sin(A)*math.sin(B) -
                  math.cos(A)*math.cos(B))
    return C
