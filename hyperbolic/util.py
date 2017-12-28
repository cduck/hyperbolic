
epsilon = 2**-30
def nearZero(val):
    return -epsilon <= val <= epsilon

def circInv(x, y, cx=0, cy=0, r=1):
    a = r**2 / ((x-cx)**2 + (y-cy)**2)
    return a*(x-cx)+cx, a*(y-cy)+cy

