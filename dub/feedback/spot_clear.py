"""Make a KNC 'after 2 weeks' still from an approved BEFORE still: fade only the dark spots on the skin, keep eyes, brows,
lips and hair sharp, add a soft morning sheen — same skin tone (luminance of clear skin is untouched).

usage: .venv/bin/python feedback/spot_clear.py <BEFORE.png> <AFTER.png>
Method: skin mask (YCrCb range) minus facial-feature edges; spots = skin pixels clearly darker than the local skin
average; spots are inpainted from surrounding skin, then a light edge-preserving smooth inside the skin only.
"""
import sys

import cv2
import numpy as np


def clear(im, thr, scale, max_frac):
    h, w = im.shape[:2]
    ycc = cv2.cvtColor(im, cv2.COLOR_BGR2YCrCb)
    skin = cv2.inRange(ycc, (40, 133, 77), (255, 178, 135))
    skin = cv2.morphologyEx(skin, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    skin = cv2.erode(skin, np.ones((7, 7), np.uint8))
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    feats = cv2.dilate(cv2.Canny(cv2.GaussianBlur(im, (5, 5), 0), 40, 110), np.ones((9, 9), np.uint8))
    big = cv2.morphologyEx(feats, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))   # eyes/brows/lips blobs
    local = cv2.GaussianBlur(gray, (0, 0), max(h, w) / scale)
    dark = ((local - gray) > thr).astype(np.uint8) * 255                               # darker than surrounding skin
    spots = cv2.bitwise_and(dark, skin)
    spots = cv2.bitwise_and(spots, cv2.bitwise_not(big))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(spots)
    keep = np.zeros_like(spots)
    max_area = h * w * max_frac                                                          # spots/patches, not features
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] <= max_area:
            keep[lab == i] = 255
    keep = cv2.dilate(keep, np.ones((5, 5), np.uint8))
    return cv2.inpaint(im, keep, 9, cv2.INPAINT_TELEA), skin, big, int(keep.sum() / 255)


def main(src, dst):
    im = cv2.imread(src)
    out, skin, big, n1 = clear(im, 9, 60, 0.004)        # small spots
    out, _, _, n2 = clear(out, 7, 30, 0.015)            # larger patches left after the first pass
    out, _, _, n3 = clear(out, 5, 20, 0.03)             # faint traces of big patches
    n2 += n3
    keep = np.full(1, (n1 + n2) * 255)
    smooth = cv2.bilateralFilter(out, 9, 28, 9)                                        # light, skin-only
    m = cv2.GaussianBlur(cv2.bitwise_and(skin, cv2.bitwise_not(big)), (0, 0), 6).astype(np.float32)[..., None] / 255
    out = (smooth * m + out * (1 - m)).astype(np.float32)
    sheen = cv2.GaussianBlur(out, (0, 0), 25)                                          # soft morning glow on luma
    yo = cv2.cvtColor(out.clip(0, 255).astype(np.uint8), cv2.COLOR_BGR2YCrCb).astype(np.float32)
    ys = cv2.cvtColor(sheen.clip(0, 255).astype(np.uint8), cv2.COLOR_BGR2YCrCb).astype(np.float32)
    a, b = yo[..., 0] / 255, ys[..., 0] / 255
    soft = np.where(b < 0.5, 2 * a * b + a * a * (1 - 2 * b), 2 * a * (1 - b) + np.sqrt(a) * (2 * b - 1))
    yo[..., 0] = (0.6 * a + 0.4 * soft) * 255
    res = cv2.cvtColor(yo.clip(0, 255).astype(np.uint8), cv2.COLOR_YCrCb2BGR)
    cv2.imwrite(dst, res)
    print(f"{dst}: {int(keep.sum() / 255)} spot px inpainted")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
