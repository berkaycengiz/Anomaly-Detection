from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

import numpy as np
import cv2
import tensorflow as tf

def _run(cmd: List[str]) -> None:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}")

def _extract_wav_16k_mono(video_path: str, wav_path: str, ffmpeg_path: str = "ffmpeg") -> None:
    cmd = [
        ffmpeg_path, "-y",
        "-i", video_path,
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-loglevel", "error",
        wav_path,
    ]
    _run(cmd)


def _read_video_frames_target_fps(video_path: str, target_fps: int = 24) -> np.ndarray:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    src_fps = cap.get(cv2.CAP_PROP_FPS)
    if not src_fps or src_fps <= 1e-3:
        src_fps = float(target_fps)

    frames = []
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        frames.append(fr)
    cap.release()

    if not frames:
        raise RuntimeError(f"No frames decoded: {video_path}")

    frames = np.stack(frames, axis=0)
    frames = frames[..., ::-1].copy()  # BGR -> RGB

    n = frames.shape[0]
    duration = n / src_fps
    t = np.arange(0.0, duration, 1.0 / target_fps)
    idx = np.clip((t * src_fps).astype(np.int64), 0, n - 1)

    idx2 = [int(idx[0])]
    for k in idx[1:]:
        k = int(k)
        if k != idx2[-1]:
            idx2.append(k)

    return frames[np.array(idx2)].astype(np.uint8)


def _resize_short_side(frames: np.ndarray, short_side: int = 256) -> np.ndarray:
    T, H, W, _ = frames.shape
    if min(H, W) == short_side:
        return frames
    if H < W:
        new_h = short_side
        new_w = int(round(W * (short_side / H)))
    else:
        new_w = short_side
        new_h = int(round(H * (short_side / W)))

    out = np.empty((T, new_h, new_w, 3), dtype=np.uint8)
    for i in range(T):
        out[i] = cv2.resize(frames[i], (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    return out


def _five_crop(frames: np.ndarray, crop_size: int = 224) -> List[np.ndarray]:
    T, H, W, _ = frames.shape
    if H < crop_size or W < crop_size:
        raise ValueError(f"Frame too small for crop: HxW={H}x{W}, crop={crop_size}")
    tl = frames[:, 0:crop_size, 0:crop_size, :]
    tr = frames[:, 0:crop_size, W - crop_size:W, :]
    bl = frames[:, H - crop_size:H, 0:crop_size, :]
    br = frames[:, H - crop_size:H, W - crop_size:W, :]
    cy = (H - crop_size) // 2
    cx = (W - crop_size) // 2
    cc = frames[:, cy:cy + crop_size, cx:cx + crop_size, :]
    return [tl, tr, bl, br, cc]


def _sliding_windows(num_frames: int, window: int, stride: int) -> List[Tuple[int, int]]:
    if num_frames < window:
        return [(0, num_frames)]
    out = []
    for s in range(0, num_frames - window + 1, stride):
        out.append((s, s + window))
    return out

class I3DVideoEmbedder:
    def __init__(self, model_dir: str, tags=None):
        if tags is None:
            tags = []
        self.model = tf.saved_model.load(model_dir, tags=tags)
        if "video" not in self.model.signatures:
            raise RuntimeError(f"'video' signature not found. Available: {list(self.model.signatures.keys())}")
        self.fn = self.model.signatures["video"]

    def embed_mixed_5c(self, clip_rgb_uint8: np.ndarray) -> np.ndarray:
        x = tf.convert_to_tensor(clip_rgb_uint8, dtype=tf.float32) / 255.0
        x = tf.expand_dims(x, axis=0)
        out = self.fn(images=x)
        y = tf.convert_to_tensor(out["mixed_5c"])  # mixed_5c is the one that gives (1,1024) shape output we need
        return y[0].numpy().astype(np.float32)

def _load_vggish(vggish_dir: str):
    sys.path.insert(0, vggish_dir)
    import vggish_input  # type: ignore
    import vggish_slim  # type: ignore
    return vggish_input, vggish_slim


def _vggish_embeddings_from_wav(wav_path: str, vggish_dir: str, ckpt_path: str) -> np.ndarray:
    vggish_input, vggish_slim = _load_vggish(vggish_dir)

    tf.compat.v1.reset_default_graph()
    with tf.compat.v1.Graph().as_default(), tf.compat.v1.Session() as sess:
        vggish_slim.define_vggish_slim(training=False)
        vggish_slim.load_vggish_slim_checkpoint(sess, ckpt_path)

        features = vggish_input.wavfile_to_examples(wav_path)  # (N,96,64)
        input_tensor = tf.compat.v1.get_default_graph().get_tensor_by_name("vggish/input_features:0")
        embedding_tensor = tf.compat.v1.get_default_graph().get_tensor_by_name("vggish/embedding:0")

        emb = sess.run(embedding_tensor, feed_dict={input_tensor: features})
    return emb.astype(np.float32)

@dataclass
class FeatureExtractorConfig:
    milnce_model_dir: str
    vggish_dir: str
    vggish_ckpt: str
    ffmpeg_path: str = "ffmpeg"
    fps: int = 24
    clip_len: int = 16
    stride: int = 16
    short_side: int = 256
    crop_size: int = 224
    savedmodel_tags: Tuple[str, ...] = ()


class FeatureExtractor:
    def __init__(self, cfg: FeatureExtractorConfig):
        self.cfg = cfg
        tags = list(cfg.savedmodel_tags) if cfg.savedmodel_tags else []
        self.visual = I3DVideoEmbedder(cfg.milnce_model_dir, tags=tags)

    def extract_rgb_5crop(self, video_path: str) -> List[np.ndarray]:
        frames = _read_video_frames_target_fps(video_path, target_fps=self.cfg.fps)
        frames = _resize_short_side(frames, short_side=self.cfg.short_side)
        crops = _five_crop(frames, crop_size=self.cfg.crop_size)

        outputs: List[np.ndarray] = []
        for crop_frames in crops:
            windows = _sliding_windows(crop_frames.shape[0], window=self.cfg.clip_len, stride=self.cfg.stride)
            feats = []
            for (s, e) in windows:
                clip = crop_frames[s:e]
                if clip.shape[0] < self.cfg.clip_len:
                    pad_n = self.cfg.clip_len - clip.shape[0]
                    clip = np.concatenate([clip, np.repeat(clip[-1:], pad_n, axis=0)], axis=0)
                feats.append(self.visual.embed_mixed_5c(clip)) 
            outputs.append(np.stack(feats, axis=0).astype(np.float32))
        return outputs

    def extract_audio(self, video_path: str) -> np.ndarray:
        with tempfile.TemporaryDirectory() as td:
            wav_path = os.path.join(td, "tmp.wav")
            _extract_wav_16k_mono(video_path, wav_path, ffmpeg_path=self.cfg.ffmpeg_path)
            return _vggish_embeddings_from_wav(wav_path, self.cfg.vggish_dir, self.cfg.vggish_ckpt)

    def extract(self, video_path: str) -> Dict[str, object]:
        rgb_5 = self.extract_rgb_5crop(video_path)
        aud = self.extract_audio(video_path)
        return {"rgb_5crop": rgb_5, "audio": aud}