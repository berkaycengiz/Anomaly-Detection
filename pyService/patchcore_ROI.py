import cv2
import numpy as np
import os
import patchcore_config

def extract_wood_roi(img, remove_side_noise=True):
    """
    Automatically extracts the vertical wood plank region.
    img: BGR image
    """

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # -------------------------------
    # 1) Horizontal projection (mean of each row)
    # -------------------------------
    proj = gray.mean(axis=1)  # shape: H

    # Normalize projection to 0-1
    proj_norm = (proj - proj.min()) / (proj.max() - proj.min() + 1e-6)

    # Smooth for stability
    proj_smooth = cv2.GaussianBlur(proj_norm.reshape(-1,1), (1, 51), 0).flatten()

    # -------------------------------
    # 2) Threshold automatically
    #    Wood rows have higher brightness; background is darker.
    # -------------------------------
    thr = 0.2 * proj_smooth.max()
    mask_rows = proj_smooth > thr

    # -------------------------------
    # 3) Largest continuous region = wood area
    # -------------------------------
    idx = np.where(mask_rows)[0]

    if len(idx) == 0:  # fallback
        return img

    # Group into contiguous segments
    splits = np.split(idx, np.where(np.diff(idx) != 1)[0] + 1)
    longest = max(splits, key=len)
    y1, y2 = longest[0], longest[-1]

    # -------------------------------
    # 4) Hard crop ROI
    # -------------------------------
    splits = np.split(idx, np.where(np.diff(idx) != 1)[0] + 1)
    longest = max(splits, key=len)
    y1, y2 = longest[0], longest[-1]
    roi = img[y1:y2, :, :]

    # Optional noise removal on left/right
    if remove_side_noise:
        # Vertical projection to remove background noise on sides
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        vproj = gray_roi.mean(axis=0)  # shape: W
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

    return roi

output_folder_path = "C:/Users/Win10/Desktop/Surface-Detection-Git/Dataset/wood/train/good_roi"
os.makedirs(output_folder_path, exist_ok=True)

for filename in os.listdir("C:/Users/Win10/Desktop/Surface-Detection-Git/Dataset/wood/train/good__"):
    img_path = os.path.join("C:/Users/Win10/Desktop/Surface-Detection-Git/Dataset/wood/train/good__", filename)
    img = cv2.imread(img_path)
    img_processed = extract_wood_roi(img, remove_side_noise=True)
    out_path = os.path.join(output_folder_path, filename)
    cv2.imwrite(out_path, img_processed)
