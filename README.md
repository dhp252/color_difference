The Color Difference Implementations
===========

## Purpose
How to measure differences between colors that near linear to human perception.


## Including:
- CIE Delta Lab / CIE E76 / dE76: Simple, error prone
- CIE Delta E2000 / CIEDE2000 / dE00: Slightly complicated, more accurate

## Perception ranges:
- Larger deltas means more noticeable
- dE76: ~ 2.3 corresponds to a JND (just noticeable difference).
- dE00:
    - <= 1.0: Not perceptible by human eyes.
    - 1 - 2: Perceptible through close observation.
    - 2 - 10: Perceptible at a glance.
    - 11 - 49: Colors are more similar than opposite
    - 100: Colors are exact opposite

## Installation
- Python 3
- cv2 >=3

## Important
- This module works mainly with OpenCV, so the input color channel for delta functions are in BGR color space.
- This module use OpenCV merely as a color space translator from BGR => XYZ => Lab. 
- Read doctring of the wrapper `_cvt_bgr2lab` function before reuse it outside this module.


## Reference:
- http://zschuessler.github.io/DeltaE/learn/
- https://www.wikiwand.com/en/Color_difference
- [Sharma 2005](https://onlinelibrary.wiley.com/doi/abs/10.1002/col.20070)
- http://www.colorwiki.com/wiki/Delta_E:_The_Color_Difference
