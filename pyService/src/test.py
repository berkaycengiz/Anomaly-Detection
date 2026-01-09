#!/usr/bin/env python3
from __future__ import annotations

import argparse
from extract_feature import FeatureExtractorConfig
from inference import InferenceConfig, ViolenceInferenceService


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video_path", type=str, default="C:\\Users\\Win10\\Videos\\2025-12-23 07-10-00.mkv")
    ap.add_argument("--ckpt", type=str, default="C:\\Users\\Win10\\Desktop\\DeepLearning\\Project\\Smart-City-Violation-Detection\\checkpoints\\TrueTrueFalsebest_model.pth")

    ap.add_argument("--milnce_model_dir", type=str, default="C:\\Users\\Win10\\Desktop\\DeepLearning\\Project\\Smart-City-Violation-Detection\\third_party\\milnce-i3d")
    ap.add_argument("--vggish_dir", type=str, default="C:\\Users\\Win10\\Desktop\\DeepLearning\\Project\\Smart-City-Violation-Detection\\third_party\\vggish")
    ap.add_argument("--vggish_ckpt", type=str, default="C:\\Users\\Win10\\Desktop\\DeepLearning\\Project\\Smart-City-Violation-Detection\\third_party\\vggish\\checkpoints\\vggish_model.ckpt")
    ap.add_argument("--ffmpeg_path", type=str, default="D:\\Yedek\\JS\\Anomaly-Detection\\pyService\\Smart-City-Violation-Detection\\ffmpeg.exe")

    ap.add_argument("--threshold", type=float, default=0.35)
    ap.add_argument("--device", type=str, default="cuda")

    ap.add_argument("--is_audio", type=bool, default=True)
    ap.add_argument("--is_visual", type=bool, default=True)
    ap.add_argument("--is_motion", type=bool, default=False)
    args = ap.parse_args()

    feat_cfg = FeatureExtractorConfig(
        milnce_model_dir=args.milnce_model_dir,
        vggish_dir=args.vggish_dir,
        vggish_ckpt=args.vggish_ckpt,
        ffmpeg_path=args.ffmpeg_path,
    )
    inf_cfg = InferenceConfig(
        ckpt_path=args.ckpt,
        device=args.device,
        is_audio=bool(args.is_audio),
        is_visual=bool(args.is_visual),
        is_motion=bool(args.is_motion),
        threshold=args.threshold,
    )

    service = ViolenceInferenceService(feat_cfg, inf_cfg)
    res = service.predict_video(args.video_path)
    print(res)


if __name__ == "__main__":
    main()