import os
import torch
import numpy as np
from tqdm import tqdm
from sklearn.metrics import roc_auc_score, f1_score

from patchcore_dataset import TestImageDataset
from patchcore_model import PatchCoreWRN50
import patchcore_config
from patchcore_heatmap import make_and_save_heatmap
import cv2


def compute_metrics(labels, scores):
    auc = roc_auc_score(labels, scores)
    
    thresh = np.percentile(scores, 22)
    preds = (scores >= thresh).astype(int)
    f1 = f1_score(labels, preds)
    
    return auc, f1, thresh, preds


def generate_heatmap(img, patch_scores, fmap_size=7):
    
    P = patch_scores.shape[0]
    if P != fmap_size * fmap_size:
        raise ValueError("Patch count mismatch for heatmap")

    heat = patch_scores.reshape(fmap_size, fmap_size)

    heat = cv2.resize(
        heat,
        (img.shape[2], img.shape[1]),
        interpolation=cv2.INTER_CUBIC
    )

    heat_norm = (heat - heat.min()) / (heat.max() - heat.min() + 1e-6)
    heat_uint8 = (heat_norm * 255).astype(np.uint8)

    return heat_uint8


def test_patchcore():
    device = patchcore_config.DEVICE

    model = PatchCoreWRN50(device=device, coreset_size=patchcore_config.CORESET)
    model.to(device)

    ckpt_path = patchcore_config.MODEL_PATH
    checkpoint = torch.load(ckpt_path, map_location=device)
    model.memory_bank = checkpoint["memory_bank"].to(device)
    
    print(f"\nDevice in use: {device}")
    print(f"Loaded memory bank: {model.memory_bank.shape}")

    good_ds = TestImageDataset(patchcore_config.TEST_GOOD_FOLDER)
    defect_ds = TestImageDataset(patchcore_config.TEST_DEFECT_FOLDER)

    print(f"Test good: {len(good_ds)}, defect: {len(defect_ds)}")

    good_scores = []
    defect_scores = []

    print("Testing GOOD images...")
    for i, img in enumerate(tqdm(good_ds)):
        img_batch = img.unsqueeze(0).to(device)

        patch_scores, img_score, H_fmap, W_fmap = model(img_batch)
        good_scores.append(img_score)

        save_path = patchcore_config.OUT_PATH_GOOD + "/" + str(i) + ".bmp"

        make_and_save_heatmap(img_tensor=img_batch, patch_scores=patch_scores, fmap_h=H_fmap, fmap_w=W_fmap, save_path=save_path)

    print("Testing DEFECT images...")
    for i, img in enumerate(tqdm(defect_ds)):
        img_batch = img.unsqueeze(0).to(device)

        patch_scores, img_score, H_fmap, W_fmap = model(img_batch)
        defect_scores.append(img_score)

        save_path = patchcore_config.OUT_PATH_DEF + "/" + str(i) + ".bmp"

        make_and_save_heatmap(img_tensor=img_batch, patch_scores=patch_scores, fmap_h=H_fmap, fmap_w=W_fmap, save_path=save_path)

    labels = np.array([0]*len(good_scores) + [1]*len(defect_scores))
    scores = np.array(good_scores + defect_scores)

    auc, f1, thresh, preds = compute_metrics(labels, scores)

    print(f"\nAUC: {auc:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"Threshold: {thresh:.4f}")

    return auc, f1, scores, labels, thresh