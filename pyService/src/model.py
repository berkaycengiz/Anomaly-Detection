import torch
from torch import nn
import torch.nn.functional as F

class TemporalAttention(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.attn = nn.Sequential(
            nn.Linear(input_dim, input_dim // 2),
            nn.ReLU(),
            nn.Linear(input_dim // 2, 1)
        )

    def forward(self, x):
        scores = self.attn(x)              # (B, T, 1)
        weights = F.softmax(scores, dim=1)
        out = (weights * x).sum(dim=1)     # (B, D)
        return out
    
class ModalityGating(nn.Module):
    def __init__(self, input_dim, num_modalities):
        super().__init__()
        self.gate = nn.Sequential(
            nn.Linear(input_dim, num_modalities),
            nn.Softmax(dim=1)
        )

    def forward(self, features):
        concat = torch.cat(features, dim=1)
        weights = self.gate(concat)

        gated = []
        for i, feat in enumerate(features):
            gated.append(feat * weights[:, i:i+1])

        return torch.cat(gated, dim=1)
    
class AudioAgent(nn.Module):
    def __init__(self):
        super().__init__()
        self.tmprl_attn = TemporalAttention(input_dim=128)

        self.mlp = nn.Sequential(
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
        )

    def forward(self, x):
        x = self.tmprl_attn(x)
        x = self.mlp(x)
        return x

class VisualAgent(nn.Module):
    def __init__(self):
        super().__init__()
        self.tmprl_attn = TemporalAttention(input_dim=1024)

        self.mlp = nn.Sequential(
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
        )

    def forward(self, x): # (B, T, 1024) -> (B, 256)
        x = self.tmprl_attn(x)
        x = self.mlp(x)
        return x
    
class MotionAgent(nn.Module):
    def __init__(self):
        super().__init__()
        self.tmprl_attn = TemporalAttention(input_dim=1024)

        self.mlp = nn.Sequential(
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
        )

    def forward(self, x): # (B, T, 1024) -> (B, 256)
        x = self.tmprl_attn(x)
        x = self.mlp(x)
        return x
    
class DecisionAgent(nn.Module):
    def __init__(self, is_audio=True, is_visual=True, is_motion=True):
        super().__init__()

        self.is_audio = is_audio
        self.is_visual = is_visual
        self.is_motion = is_motion

        self.feature_dims = []
        self.total_dim = 0

        if self.is_audio:
            self.feature_dims.append(128)
            self.total_dim += 128
        if self.is_visual:
            self.feature_dims.append(256)
            self.total_dim += 256
        if self.is_motion:
            self.feature_dims.append(256)
            self.total_dim += 256

        self.gating = ModalityGating(input_dim=self.total_dim, num_modalities=len(self.feature_dims))

        self.classifier = nn.Sequential(
            nn.Linear(self.total_dim, self.total_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(self.total_dim // 2, self.total_dim // 4),
            nn.ReLU(),
            nn.Linear(self.total_dim // 4, 1)
            )

    def forward(self, f_audio = None, f_rgb = None, f_flow = None):

        features = []
        if f_audio is not None:
            features.append(f_audio)
        if f_rgb is not None:
            features.append(f_rgb)
        if f_flow is not None:
            features.append(f_flow)
        fusion = self.gating(features)
        out = self.classifier(fusion)
        return out

class MultiAgentViolanceModel(nn.Module):
    def __init__(self, is_audio=True, is_visual=True, is_motion=True):

        super().__init__()
        
        self.is_audio = is_audio
        if is_audio:
            self.AudioAgent = AudioAgent()

        self.is_visual = is_visual
        if is_visual:
            self.VisualAgent = VisualAgent()
            
        self.is_motion = is_motion
        if is_motion:   
            self.MotionAgent = MotionAgent()

        self.DecisionAgent = DecisionAgent(is_audio=self.is_audio, is_visual=self.is_visual, is_motion=self.is_motion)

    def forward(self, audio=None, rgb=None, flow=None):

        f_audio, f_rgb, f_flow = None, None, None

        if self.is_audio:
            f_audio = self.AudioAgent(audio)
        if self.is_visual:
            f_rgb = self.VisualAgent(rgb)
        if self.is_motion:   
            f_flow = self.MotionAgent(flow)

        logits = self.DecisionAgent(f_audio, f_rgb, f_flow)
        
        return logits