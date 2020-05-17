# This module can run independently
# Clumsily implemented by Do Hong Phuong


from math import atan2, sin, cos, exp
from math import radians as rad
from math import degrees as deg

import numpy as np
import cv2

def _cvt_bgr2lab(bgr_img):
    """because OpenCV conversion function modified the final result. We use 
    this function to wrap and reverse back to the original Lab result. 
    Use in CIE E76, CIE E94, CIE E2000 formulas.
    """
    lab = cv2.cvtColor(bgr_img,cv2.COLOR_BGR2Lab)
    lab[:,:,0]     = lab[:,:,0] / 255 * 100 # L
    lab[:,:,[1,2]] = lab[:,:,[1,2]] - 128   # a, b
    return lab


def dist(p,q):
    """Calculate Euclid distance"""
    return sqrt(sum((px - qx) ** 2.0 for px, qx in zip(p, q)))


def de76(bgr1, bgr2, ret_bool:bool=False):
    """CIE Delta Lab / CIE E76 / dE76
    implement from https://www.wikiwand.com/en/Color_difference
    
    bgr1, bgr2 are lists of 3 values in BGR
    ret_bool: True if over Just-noticeable_difference values, else False
    
    example:
    bgr1 = [255,255,0]
    bgr2 = [255,0,255]
    de00 = cie00(bgr1, bgr2)
    """
    bgr1 = np.array([[bgr1]], dtype=np.uint8)
    bgr2 = np.array([[bgr2]], dtype=np.uint8)
    
    repr1 = _cvt_bgr2lab(bgr1)[0,0].tolist()
    repr2 = _cvt_bgr2lab(bgr2)[0,0].tolist()
    
    delta = dist(repr1, repr2)
    
    if ret_bool:
        noticable_diff = delta >= 2.3
        return delta, noticable_diff
    else:
        return delta
    
    
def de00(bgr1, bgr2,ret_bool:bool=False):
    """CIE Delta E2000 / CIEDE2000 / dE00
    implement from Sharma 2005    
    
    bgr1, bgr2 are lists of 3 values in BGR
    ret_bool: True if over Just-noticeable_difference values, else False
    
    Notation at the end of variable names:
    p = prime (')
    
    example:
    bgr1 = [255,255,0]
    bgr2 = [255,0,255]
    de00 = cie00(bgr1, bgr2)
    """
    bgr1 = np.array([[bgr1]], dtype=np.uint8)
    bgr2 = np.array([[bgr2]], dtype=np.uint8)
    
    lab1 = _cvt_bgr2lab(bgr1)[0,0].tolist()
    lab2 = _cvt_bgr2lab(bgr2)[0,0].tolist()
    
    L1, a1, b1 = lab1[0], lab1[1], lab1[2]
    L2, a2, b2 = lab2[0], lab2[1], lab2[2]
    
    ##### CALCULATE Ci_p , hi_p
    # (2) 
    C1 = (a1**2 + b1**2) ** 0.5
    C2 = (a2**2 + b2**2) ** 0.5
    
    # (3)
    mean_C = (C1 + C2) / 2
    
    # (4)
    G = 0.5 * (1 - (mean_C**7 / (mean_C**7 + 25**7))**0.5)
    
    # (5)
    a1_p = (1+G)*a1
    a2_p = (1+G)*a2
    
    # (6)
    C1_p = (a1_p**2 + b1**2) ** 0.5
    C2_p = (a2_p**2 + b2**2) ** 0.5
    
    # (7)
    h1_p = deg(atan2(b1,a1_p)) % 360
    h2_p = deg(atan2(b2,a2_p)) % 360 
        
    ##### CALCULATE Delta(s) of L, C, H
    # (8)
    delta_L_p = L2 - L1
    
    # (9)
    delta_C_p = C2_p - C1_p
    
    # (10)
    raw_delta_h = h2_p - h1_p
    abs_delta_h = abs(raw_delta_h)
    
    if C1_p * C2_p == 0:
        delta_h_p = 0
    elif abs_delta_h <= 180:
        delta_h_p = raw_delta_h
    elif raw_delta_h > 180:
        delta_h_p = raw_delta_h - 360
    elif raw_delta_h < -180:
        delta_h_p = raw_delta_h + 360
        
    # (11)
    delta_H_p = (C1_p * C2_p) ** 0.5 * sin( rad(delta_h_p) /2 ) * 2
    
    ##### CALCULATE CIE E2000
    # (12)
    mean_L_p = (L1 + L2) / 2
    
    # (13)
    mean_C_p = (C1_p + C2_p) / 2
    
    # (14)
    sum_h_p = h1_p + h2_p
    
    if C1_p * C2_p == 0:
        mean_h_p = sum_h_p
    elif abs_delta_h <= 180:
        mean_h_p = sum_h_p / 2
    elif sum_h_p < 360:
        mean_h_p = (sum_h_p + 360 ) / 2
    elif sum_h_p >= 360:
        mean_h_p = (sum_h_p - 360 ) / 2
    
    # (15)
    T  = 1 - 0.17*cos(rad(mean_h_p - 30)) + 0.24*cos(rad(2*mean_h_p))
    T += 0.32*cos(rad(3*mean_h_p+6)) - 0.2*cos(rad(4*mean_h_p-63))
    
    # (16)
    delta_theta = 30*exp(-((mean_h_p - 275) / 25 )**2)
    
    # (17)
    Rc = 2 * (mean_C_p**7 / (mean_C_p**7 + 25**7))**0.5
    
    # (18)
    Sl = 1 + (0.015 * (mean_L_p - 50)**2 ) / (20+ (mean_L_p - 50)**2) ** 0.5
    
    # (19)
    Sc = 1 + 0.045 * mean_C_p
    
    # (20)
    Sh = 1 + 0.015 * mean_C_p * T
    
    # (21)
    Rt = -sin( rad(2 * delta_theta) ) * Rc
    
    # (22)
    kl = kc = kh = 1 # Unity by default
    delta_E2000  = (delta_L_p / (kl * Sl)) ** 2 
    delta_E2000 += (delta_C_p / (kc * Sc)) ** 2 
    delta_E2000 += (delta_H_p / (kh * Sh)) ** 2 
    delta_E2000 += Rt * (delta_C_p / (kc * Sc)) * (delta_H_p / (kh * Sh))
    delta_E2000 **= 0.5
    
    if ret_bool:
        noticable_diff = delta_E2000 >= 2
        return delta_E2000, noticable_diff
    else:
        return delta_E2000


if __name__=='__main__':
    bgr1 = [255,255,0]
    bgr2 = [255,0,255]
    diff = de00(bgr1, bgr2)
    print(diff)