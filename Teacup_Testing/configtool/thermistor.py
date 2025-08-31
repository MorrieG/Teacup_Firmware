from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from builtins import object
from past.utils import old_div
from math import *
import sys


class SHThermistor(object):
  def __init__(self, rp, t0, r0, t1, r1, t2, r2):
    self.rp = rp

    self.paramsOK = True
    try:
      T0 = t0 + 273.15;   T1 = t1 + 273.15;   T2 = t2 + 273.15
      a0 = log(r0);       a1 = log(r1);       a2 = log(r2)
      z = a0 - a1
      y = a0 - a2
      x = old_div(1, T0) - old_div(1, T1)
      w = old_div(1, T0) - old_div(1, T2)
      v = a0 ** 3 - a1 ** 3
      u = a0 ** 3 - a2 ** 3

      self.C = old_div((x - old_div(z * w, y)), (v - old_div(z * u, y)))
      self.B = old_div((x - self.C * v), z)
      self.A = old_div(1, T0) - self.C * a0 ** 3 - self.B * a0
    except:
      self.paramsOK = False

  def setting(self, t):
    if not self.paramsOK:
      return None, None

    try:
      T = t + 273.15
      y = old_div((self.A - old_div(1,T)), self.C)
      x = ((old_div(self.B, (3 * self.C))) ** 3 + old_div((y ** 2), 4)) ** 0.5
      r = exp((x - old_div(y, 2)) ** (1.0/3) - (x + old_div(y, 2)) ** (1.0/3))
      return self.adc(r), r
    except:
      return None, None

  def temp(self, adc):
    r = self.adcInv(adc)
    t = (1.0 / (self.A + self.B * log(r) + self.C * (log(r) ** 3))) - 273.15;
    return t

  def adc(self, r):
    return 1023.0 * r / (r + self.rp)

  def adcInv(self, adc):
    return old_div((self.rp * adc),(1023.0 - adc))

class BetaThermistor(object):
  def __init__(self, r0, t0, beta, r1, r2, vadc):
    self.paramsOK = True

    try:
      self.r0 = r0
      self.t0 = t0 + 273.15
      self.beta = beta
      self.vadc = vadc
      self.k = r0 * exp(old_div(-beta, self.t0))

      if r1 > 0:
        self.vs = old_div(r1 * self.vadc, (r1 + r2))
        self.rs = old_div(r1 * r2, (r1 + r2))
      else:
        self.vs = self.vadc
        self.rs = r2
    except:
      self.paramsOK = False

  def temp(self, adc):
    v = old_div(adc * self.vadc, 1024)
    if (self.vs - v):
      r = old_div(self.rs * v, (self.vs - v))
    else:
      r = self.r0 * 10
    try:
      return (old_div(self.beta, log(old_div(r, self.k)))) - 273.15
    except:
      print("// error for ADC = {adc}, {v}, {r}".format(adc = adc, v = v, r = r))
      return None

  def resistance(self, t):
    return self.r0 * exp(self.beta * (old_div(1, (t + 273.15)) - old_div(1, self.t0)))

  def setting(self, t):
    if not self.paramsOK:
      return None, None

    try:
      r = self.r0 * exp(self.beta * (old_div(1, (t + 273.15)) - old_div(1, self.t0)))
      v = old_div(self.vs * r, (self.rs + r))
      return round(old_div(v, self.vadc * 1024)), r
    except:
      return None, None

  def adcInv(self, adc):
    return (adc * self.vadc)/1024.0
