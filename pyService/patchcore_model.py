import torch
import torch.nn as nn
from torchvision import models
from patchcore_config import TOPK
import torch.nn.functional as F


class PatchCoreWRN50(nn.Module):
    def __init__(self, device="cuda", coreset_size=0.2):
        super().__init__()
        self.device = device
        self.coreset_size = coreset_size
        
        #using pretrained model
        wrn = models.wide_resnet50_2(weights=models.Wide_ResNet50_2_Weights.IMAGENET1K_V1)
        
        #structure of WRN50 in simple
        self.conv1 = wrn.conv1
        self.bn1 = wrn.bn1
        self.relu = wrn.relu
        self.maxpool = wrn.maxpool
        self.layer1 = wrn.layer1
        self.layer2 = wrn.layer2
        self.layer3 = wrn.layer3
        self.layer4 = wrn.layer4
        
        #closing backpropogation since ve do not train the model
        self.eval()
        for p in self.parameters():
            p.requires_grad = False

        self.memory_bank = None

    def extract_features(self, images):

        #applyin model to image and taikng layer feats
        with torch.no_grad():
            x = self.conv1(images)
            x = self.bn1(x)
            x = self.relu(x)
            x = self.maxpool(x)
            x1 = self.layer1(x)
            x2 = self.layer2(x1)
            x3 = self.layer3(x2)
            x4 = self.layer4(x3)

        #try between x2 and x3 as target size
        h_target, w_target = x3.shape[2], x3.shape[3]

        #dont forget to change the interpolatin if you change taraget size
        x2_up = F.interpolate(x2, size=(h_target, w_target), mode="bilinear", align_corners=False)
        x3_up = x3  # zaten hedef boyutta
        x4_up = F.interpolate(x4, size=(h_target, w_target), mode="bilinear", align_corners=False)

        #to use all layers we put them in a feat (try different variations)
        feat = torch.cat([x2_up, x3_up, x4_up], dim=1)
        
        B, C, H, W = feat.shape
        fmap_flat = feat.permute(0, 2, 3, 1).reshape(B, H*W, C)

        return fmap_flat, H, W

    def build_memory_bank(self, feature_list):
        all_features = torch.cat(feature_list, dim=0)
        total = all_features.shape[0]
        keep = int(total * self.coreset_size)

        print(f"Total patches: {total}, CoreSet keep: {keep}")

        idxs = torch.randperm(total)[:keep]
        self.memory_bank = all_features[idxs].to(self.device)

    def anomaly_score_patchwise(self, patch_feats, chunk_size=512):
        patch_feats = patch_feats.to(self.device)
        memory = self.memory_bank.to(self.device)
    
        patch_feats = patch_feats / (patch_feats.norm(dim=1, keepdim=True) + 1e-6)
        memory = memory / (memory.norm(dim=1, keepdim=True) + 1e-6)
    
        min_dists = []
    
        for i in range(0, memory.shape[0], chunk_size):
            mb_chunk = memory[i:i + chunk_size]
            sim_chunk = torch.mm(patch_feats, mb_chunk.t())
            dist_chunk = 1.0 - sim_chunk
            min_dists.append(dist_chunk.min(dim=1)[0].cpu())
    
        return torch.stack(min_dists, dim=1).min(dim=1)[0]

    #takes top k anormal patches scores to send them to metrics
    def forward(self, img, topk=TOPK):
        feats, H, W = self.extract_features(img)
        feats_0 = feats[0]
        patch_scores = self.anomaly_score_patchwise(feats_0)

        if topk is None:
            image_score = patch_scores.max().item()
        else:
            k = min(topk, patch_scores.numel())
            topk_vals, _ = torch.topk(patch_scores, k)
            image_score = topk_vals.mean().item()

        return patch_scores, image_score, H, W