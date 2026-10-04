import cv2
import numpy as np

W, H = 1920, 1080
FX = (W / 2) / np.tan(np.radians(86 / 2))
K = np.array([[FX, 0, W / 2], [0, FX, H / 2], [0, 0, 1]])


def homographie(d_mm, angle_deg, l_mm, h_mm, mm_px):
    a = np.radians(angle_deg)
    R = np.array([[np.cos(a), 0, np.sin(a)],
                  [0, 1, 0],
                  [-np.sin(a), 0, np.cos(a)]])
    t = np.array([0, 0, d_mm])
    S = np.array([[1 / mm_px, 0, -l_mm / 2],
                  [0, 1 / mm_px, -h_mm / 2],
                  [0, 0, 1]])
    return K @ np.column_stack([R[:, 0], R[:, 1], t]) @ S


def photographier(plan, d_mm, angle_deg, l_mm, h_mm, mm_px):
    Hm = homographie(d_mm, angle_deg, l_mm, h_mm, mm_px)
    return cv2.warpPerspective(plan, Hm, (W, H), borderValue=(120, 120, 120))