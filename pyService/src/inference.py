from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import numpy as np
import torch
from extract_feature import FeatureExtractor, FeatureExtractorConfig
from model import MultiAgentViolanceModel

@dataclass
class InferenceConfig:
    ckpt_path: str
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    is_audio: bool = True
    is_visual: bool = True
    is_motion: bool = False
    threshold: float = 0.5


class ViolenceInferenceService:

    def __init__(self, feat_cfg: FeatureExtractorConfig, inf_cfg: InferenceConfig):
        self.fe = FeatureExtractor(feat_cfg)
        self.inf_cfg = inf_cfg
        self.device = torch.device(inf_cfg.device)

        self.model = MultiAgentViolanceModel(
            is_audio=inf_cfg.is_audio,
            is_visual=inf_cfg.is_visual,
            is_motion=inf_cfg.is_motion,
        ).to(self.device).eval()

        sd = torch.load(inf_cfg.ckpt_path, map_location=self.device)
        try:
            self.model.load_state_dict(sd, strict=True)
        except RuntimeError:
            sd2 = {k.replace("module.", ""): v for k, v in sd.items()}
            self.model.load_state_dict(sd2, strict=False)

    @staticmethod
    def _avg_5crop(rgb_5crop: List[np.ndarray]) -> np.ndarray:
        T = min(x.shape[0] for x in rgb_5crop)
        arr = np.stack([x[:T] for x in rgb_5crop], axis=0)
        return arr.mean(axis=0).astype(np.float32)

    def _to_bt(self, x: np.ndarray) -> torch.Tensor: # (T,D) -> (1,T,D)     
        return torch.from_numpy(x).unsqueeze(0).to(self.device) 

    @torch.inference_mode()
    def predict_video(self, video_path: str) -> Dict[str, Any]:
        feats = self.fe.extract(video_path)

        rgb_5: List[np.ndarray] = feats["rgb_5crop"]
        aud: np.ndarray = feats["audio"]

        rgb_avg = self._avg_5crop(rgb_5) if self.inf_cfg.is_visual else None
        aud_x = aud if self.inf_cfg.is_audio else None

        print(f"Extracted features for {video_path}:")
        print(f"  RGB shape: {rgb_avg.shape if rgb_avg is not None else None}")
        print(f"  Audio shape: {aud_x.shape if aud_x is not None else None}")

        audio_t = None if aud_x is None else self._to_bt(aud_x)
        rgb_t = None if rgb_avg is None else self._to_bt(rgb_avg)
        flow_t = None  # flow features doesn't add much but takes so much time to extract so we skip it

        logits = self.model(audio=audio_t, rgb=rgb_t, flow=flow_t)

        print(f"Shapes after model inference:")
        print(f"  Logits shape: {logits.shape}")

        if logits.dim() == 2 and logits.shape[0] == 1 and logits.shape[1] == 1:
            logits = logits.view(1)
        if logits.dim() == 2 and logits.shape[0] == 1:
            probs = torch.sigmoid(logits).squeeze(0).detach().cpu().numpy()
            violence_prob = float(probs[-1])  # if multi-label, take last as "violence" (adjust if needed)
        else:
            prob = torch.sigmoid(logits).detach().cpu().numpy()
            violence_prob = float(prob.reshape(-1)[0])

        is_violence = violence_prob >= self.inf_cfg.threshold

        return {
            "video_path": video_path,
            "violence_prob": violence_prob,
            "is_violence": is_violence,
        }