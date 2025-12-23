import cv2
import numpy as np
import torch


def make_and_save_heatmap(img_tensor: torch.Tensor, patch_scores: torch.Tensor, fmap_h: int, fmap_w: int, save_path: str = "heatmap.bmp"):

    if img_tensor.dim() == 4:
        img = img_tensor.squeeze(0)
    else:
        img = img_tensor
    img = img.permute(1, 2, 0).cpu().numpy()
    img = (img * 255).clip(0, 255).astype(np.uint8)

    H_img, W_img = img.shape[:2]

    if isinstance(patch_scores, torch.Tensor):
        patch_scores = patch_scores.detach().cpu().numpy()
    P = patch_scores.shape[0]
    assert P == fmap_h * fmap_w, f"Patch count dont match: {P} - {fmap_h}*{fmap_w}"

    heat = patch_scores.reshape(fmap_h, fmap_w)

    heat_up = cv2.resize(heat.astype(np.float32), (W_img, H_img), interpolation=cv2.INTER_CUBIC)

    low = np.percentile(heat_up, 5)
    high = np.percentile(heat_up, 95)
    heat_clipped = np.clip(heat_up, low, high)

    heat_norm = (heat_clipped - heat_clipped.min()) / (heat_clipped.max() - heat_clipped.min() + 1e-6)
    heat_uint8 = (heat_norm * 255).astype(np.uint8)

    heat_color = cv2.applyColorMap(heat_uint8, cv2.COLORMAP_INFERNO)
    overlay = cv2.addWeighted(img, 0.6, heat_color, 0.4, 0)

    cv2.imwrite(save_path.replace(".bmp", "_heatmap.bmp"), heat_color)
    cv2.imwrite(save_path.replace(".bmp", "_overlay.bmp"), overlay)

    return heat_color, overlay