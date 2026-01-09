import torch
from torch import nn
import torch.nn.functional as F

class TemporalMeanPooling(nn.Module):
    def forward(self, x):
        return x.mean(dim=1) # (B, T, D) -> (B, D)
    
class AudioAgent(nn.Module):
    def __init__(self):
        super().__init__()
        self.pool = TemporalMeanPooling()

        self.mlp = nn.Sequential(
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
        )

    def forward(self, x):
        x = self.pool(x)
        x = self.mlp(x)
        return x

class VisualAgent(nn.Module):
    def __init__(self):
        super().__init__()
        self.pool = TemporalMeanPooling()

        self.mlp = nn.Sequential(
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
        )

    def forward(self, x): # (B, T, 1024) -> (B, 256)
        x = self.pool(x)
        x = self.mlp(x)
        return x
    
class MotionAgent(nn.Module):
    def __init__(self):
        super().__init__()
        self.pool = TemporalMeanPooling()

        self.mlp = nn.Sequential(
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
        )

    def forward(self, x): # (B, T, 1024) -> (B, 256)
        x = self.pool(x)
        x = self.mlp(x)
        return x
    
class DecisionAgent(nn.Module):
    def __init__(self, is_audio=True, is_visual=True, is_motion=True):
        super().__init__()

        input_dim = 0
        if is_audio:
            input_dim += 128
        if is_visual:
            input_dim += 256
        if is_motion:
            input_dim += 256

        self.classifier = nn.Sequential(
            nn.Linear(input_dim, input_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(input_dim // 2, input_dim // 4),
            nn.ReLU(),
            nn.Linear(input_dim // 4, 1)
            )

    def forward(self, f_audio = None, f_rgb = None, f_flow = None):

        features = []
        if f_audio is not None:
            features.append(f_audio)
        if f_rgb is not None:
            features.append(f_rgb)
        if f_flow is not None:
            features.append(f_flow)
        fusion = torch.cat(features, dim=1)
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

        self.DecisionAgent = DecisionAgent(is_audio=is_audio, is_visual=is_visual, is_motion=is_motion)

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
    