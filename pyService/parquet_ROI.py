import cv2
import numpy as np

def extract_wood_roi(img_raw, remove_side_noise=True):
    
    img_cropped = img_raw[0:1000, 1700:2700]
    img_hsv_cropped = cv2.cvtColor(img_cropped, cv2.COLOR_BGR2HSV)
    
    lwr_limit = np.array([35, 51, 41])
    uppr_limit = np.array([136, 255, 151])
    
    mask = cv2.inRange(img_hsv_cropped, lwr_limit, uppr_limit)
    
    mask_inv = cv2.bitwise_not(mask)
    
    img = cv2.bitwise_and(img_cropped, img_cropped, mask=mask_inv)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    proj = gray.mean(axis=1)

    proj_norm = (proj - proj.min()) / (proj.max() - proj.min() + 1e-6)

    proj_smooth = cv2.GaussianBlur(proj_norm.reshape(-1,1), (1, 51), 0).flatten()

    thr = 0.2 * proj_smooth.max()
    mask_rows = proj_smooth > thr

    idx = np.where(mask_rows)[0]

    if len(idx) == 0:
        return img

    roi_raw = img_cropped[:, :, :]
    roi = img[:, :, :]

    if remove_side_noise:
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        vproj = gray_roi.mean(axis=0)
        vproj_norm = (vproj - vproj.min()) / (vproj.max() - vproj.min() + 1e-6)
        vproj_smooth = cv2.GaussianBlur(vproj_norm.reshape(1,-1), (51, 1), 0).flatten()

        thr2 = 0.2 * vproj_smooth.max()
        mask_cols = vproj_smooth > thr2

        idx2 = np.where(mask_cols)[0]
        if len(idx2) > 0:
            splits2 = np.split(idx2, np.where(np.diff(idx2) != 1)[0] + 1)
            longest2 = max(splits2, key=len)
            x1, x2 = longest2[0], longest2[-1]
            roi = roi[:, x1:x2]
            roi_out = roi_raw[:, x1:x2]

    return roi_out