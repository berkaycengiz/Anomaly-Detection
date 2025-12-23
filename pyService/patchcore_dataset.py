import os
import cv2
import torch
import numpy as np
from glob import glob
from torch.utils.data import Dataset
from patchcore_config import HSV_MASK, CROP_REGION
from parquet_ROI import extract_wood_roi

class TrainImageDataset(Dataset):

    def __init__(self, folder):
        self.paths = glob(os.path.join(folder, "*.bmp"))

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, idx):
        p = self.paths[idx]
        img_bgr = cv2.imread(p)

        img_roi = extract_wood_roi(img_bgr)

        img_rgb = cv2.cvtColor(img_roi, cv2.COLOR_BGR2RGB)

        img = torch.tensor(img_rgb.transpose(2,0,1), dtype=torch.float32) / 255.0
        return img


class TestImageDataset(Dataset):

    def __init__(self, folder):
        self.paths = glob(os.path.join(folder, "*.bmp"))

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, idx):
        p = self.paths[idx]
        img_bgr = cv2.imread(p)

        img_roi = extract_wood_roi(img_bgr)

        img_rgb = cv2.cvtColor(img_roi, cv2.COLOR_BGR2RGB)
        img = torch.tensor(img_rgb.transpose(2,0,1), dtype=torch.float32) / 255.0

        return img
