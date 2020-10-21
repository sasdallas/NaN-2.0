import math

class InterpolationBase:
    def apply(self, p): # percent, from 0 to 1
        return p

class Smooth(InterpolationBase):
    def apply(self, p):
        return p * p * (3 - 2 * p)

class Circle(InterpolationBase):
    def apply(self, p):
        if p <= 0.5:
            p *= 2
            return (1 - (1 - p * p) ** .5) / 2
        p -= 1
        p *= 2
        return ((1 - p * p) ** .5 + 1) / 2

class Pow(InterpolationBase):
    def __init__(self, power):
        self.power = power

    def apply(self, p):
        if p <= 0.5:
            return (p * 2) ** self.power / 2
        return ((p - 1) * 2) ** self.power / (-2 if self.power % 2 == 0 else 2) + 1

class PowIn(InterpolationBase):
    def __init__(self, power):
        self.power = power

    def apply(self, p):
        return p ** self.power

class PowOut(InterpolationBase):
    def __init__(self, power):
        self.power = power

    def apply(self, p):
        return (p - 1) ** self.power * (-1 if self.power % 2 == 0 else 1) + 1

class Sine(InterpolationBase):
    def apply(self, p):
        return (1 - math.cos(p * math.pi)) / 2
