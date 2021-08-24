import colorsys

import numpy as np
from PIL import Image


# See https://stackoverflow.com/questions/7274221/changing-image-hue-with-python-pil

def _shift_hue(arr, hout):
    r, g, b, a = np.rollaxis(arr, axis=-1)
    h, s, v = np.vectorize(colorsys.rgb_to_hsv)(r, g, b)
    h = hout
    r, g, b = np.vectorize(colorsys.hsv_to_rgb)(h, s, v)
    arr = np.dstack((r, g, b, a))
    return arr


def colorize(image, hue):
    """
    Colorize PIL image with the given ``hue``.

    Args:
        image: PIL image
        hue: number between 0–360

    Returns:
        PIL image w/ hue changed
    """
    img = image.convert('RGBA')
    arr = np.array(np.asarray(img).astype('float'))
    new_img = Image.fromarray(_shift_hue(arr, hue / 360.).astype('uint8'), 'RGBA')

    return new_img
