import torch
import numpy as np
from torchvision import transforms

TRAIN_DATA_FOLDER = "your_path"
TEST_GOOD_FOLDER   = "your_path"
TEST_DEFECT_FOLDER = "your_path"
MODEL_PATH = "your_path"
OUT_PATH_GOOD = "your_path"
OUT_PATH_DEF = "your_path"

PATCH_SIZE = 256
PATCH_STRIDE = 64
BATCH_SIZE = 16
EPOCHS = 10
LR = 1e-3
TOPK = 15
CORESET = 0.2
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
CROP_REGION = ( (0,1000), (1600,2800) )
HSV_MASK = (np.array([35,51,41]), np.array([136,255,151]))

TRAIN_TRANSFORM = transforms.Compose([
    transforms.ToPILImage(),
    transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.05, hue=0.02),
    transforms.RandomHorizontalFlip(0.5),
    transforms.RandomVerticalFlip(0.5),
    transforms.RandomRotation(degrees=(-3,3)),
    transforms.ToTensor(),
])
TEST_TRANSFORM = transforms.Compose([
    transforms.ToPILImage(),
    transforms.ToTensor(),
])