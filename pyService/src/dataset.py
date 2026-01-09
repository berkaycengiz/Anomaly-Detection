import os
import numpy as np
import torch
from torch.utils.data import Dataset


class XDViolenceDataset(Dataset):
    def __init__(self, root_dir, split="train", max_timesteps=100, data_size=19770, is_audio=True, is_visual=True, is_motion=True):
        self.root_dir = root_dir
        self.split = split
        self.max_timesteps = max_timesteps
        self.is_audio = is_audio
        self.is_visual = is_visual
        self.is_motion = is_motion
        self.data_size = data_size
        self.audio_dir, self.rgb_dir, self.flow_dir = None, None, None
        if self.is_audio and self.is_motion and self.is_visual is False:
            raise ValueError("At least one module should be activated!")
        if is_audio:
            self.audio_dir = os.path.join(root_dir, "vggish-features", split)
        if is_visual:
            self.rgb_dir = os.path.join(root_dir, "i3d-rgb-features", split)
        if is_motion:
            self.flow_dir = os.path.join(root_dir, "i3d-flow-features", split)

        self.video_ids = self.collect_video_ids()

    def __len__(self):
        return len(self.video_ids)
    
    def collect_video_ids(self):
        id_sets = []

        if self.is_audio:
            audio_ids = {
                f.replace("__vggish.npy", "")
                for i, f in enumerate(os.listdir(self.audio_dir))
                if f.endswith(".npy") and i<=self.data_size/5
            }
            id_sets.append(audio_ids)

        if self.is_visual:
            rgb_ids = set()
            for i, f in enumerate(os.listdir(self.rgb_dir)):
                if i<=self.data_size:
                    id = f.rsplit("__", 1)[0]
                    rgb_ids.add(id)
            id_sets.append(rgb_ids)

        if self.is_motion:
            flow_ids = set()
            for i, f in enumerate(os.listdir(self.flow_dir)):
                if i<=self.data_size:
                    id = f.rsplit("__",1)[0]
                    flow_ids.add(id)
            id_sets.append(flow_ids)

        return sorted(set.intersection(*id_sets))

    def _load_feature(self, path, is_multicrop=False):
        if not is_multicrop:
            path = f"{path}__vggish.npy"
            feat = np.load(path)
            T, D = feat.shape

            if T >= self.max_timesteps:
                feat = feat[:self.max_timesteps]
            else:
                pad = np.zeros((self.max_timesteps - T, D)) #pad ve mask ile deneme yap
                feat = np.concatenate([feat, pad], axis=0)
                #mask = np.zeros(self.max_timesteps)
                #mask[:min(T, self.max_timesteps)] = 1
                #feat = np.concatenate([feat, mask], axis=0)

            return torch.tensor(feat, dtype=torch.float32)
        else:
            crops=[]
            base_path = path # original path will corrupt so we use a copy
            for i in range(5):
                feat_path = f"{base_path}__{i}.npy"
                feat = np.load(feat_path)
                T, D = feat.shape
                if T >= self.max_timesteps:
                    feat = feat[:self.max_timesteps]
                else:
                    pad = np.zeros((self.max_timesteps - T, D))
                    feat = np.concatenate([feat, pad], axis=0)
                crops.append(feat)
            crops = np.stack(crops, axis=0)  # Shape: (5, max_timesteps, D)
            feat = crops.mean(axis=0)  # Average over crops, may try using 5 different agents for these crops TODO
            return torch.tensor(feat, dtype=torch.float32)

    def _parse_label(self, video_id):
        label_part = video_id.split("label_")[-1]

        # Simple binary label parsing (A: non-violence, Others: violence)
        if label_part.startswith("A"):
            return torch.tensor(0.0)
        else:
            return torch.tensor(1.0)

    def __getitem__(self, idx):
        video_id = self.video_ids[idx]

        audio_feat, rgb_feat, flow_feat = None, None, None

        if self.is_audio:
            audio_path = os.path.join(self.audio_dir, video_id)
            audio_feat = self._load_feature(audio_path, is_multicrop=False)

        if self.is_visual:
            rgb_path = os.path.join(self.rgb_dir, video_id)
            rgb_feat = self._load_feature(rgb_path, is_multicrop=True)
        if self.is_motion:
            flow_path = os.path.join(self.flow_dir, video_id)
            flow_feat = self._load_feature(flow_path, is_multicrop=True)

        label = self._parse_label(video_id)

        # Only include modalities that are actually used (not None), batch doesn't handle None
        result = {"label": label}
        if self.is_audio and audio_feat is not None:
            result["audio"] = audio_feat
        if self.is_visual and rgb_feat is not None:
            result["rgb"] = rgb_feat
        if self.is_motion and flow_feat is not None:
            result["flow"] = flow_feat

        return result