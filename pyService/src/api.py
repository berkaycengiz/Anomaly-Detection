from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import httpx
import os
import uuid
import torch
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from inference import ViolenceInferenceService, InferenceConfig
from extract_feature import FeatureExtractorConfig

app = FastAPI(title="Smart City Violation Detection API")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKPOINT_PATH = os.path.join(BASE_DIR, "checkpoints", "TrueTrueFalsebest_model.pth")
THIRD_PARTY_DIR = os.path.join(BASE_DIR, "feature_extract")

FEAT_CFG = FeatureExtractorConfig(
    milnce_model_dir=os.path.join(THIRD_PARTY_DIR, "milnce-i3d"),
    vggish_dir=os.path.join(THIRD_PARTY_DIR, "vggish"),
    vggish_ckpt=os.path.join(THIRD_PARTY_DIR, "vggish", "checkpoints", "vggish_model.ckpt"),
    ffmpeg_path="ffmpeg.exe"
)

INF_CFG = InferenceConfig(
    ckpt_path=CHECKPOINT_PATH,
    device="cuda" if torch.cuda.is_available() else "cpu",
    threshold=0.53
)

service = ViolenceInferenceService(FEAT_CFG, INF_CFG)

NODE_BACKEND_URL = "http://localhost:8080/anomaly"

class AnalyzeRequest(BaseModel):
    id: str
    videoUrl: str

async def perform_analysis(video_id: str, video_url: str):
    temp_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"processing_{uuid.uuid4()}.mp4")
    
    if not os.path.exists(FEAT_CFG.ffmpeg_path):
        print(f"[!] CRITICAL: FFMPEG not found at: {FEAT_CFG.ffmpeg_path}")
    else:
        print(f"[*] FFMPEG found at: {FEAT_CFG.ffmpeg_path}")

    try:
        async with httpx.AsyncClient() as client:
            print(f"[*] Indiriliyor: {video_url}")
            r = await client.get(video_url, timeout=120.0)
            if r.status_code == 200:
                with open(temp_name, "wb") as f:
                    f.write(r.content)
                print(f"[*] Video kaydedildi: {temp_name} ({os.path.getsize(temp_name)} bytes)")
            else:
                raise Exception(f"Indirme hatasi: {r.status_code}")

        print(f"[*] Analiz basladi: {video_id}")
        if not os.path.exists(temp_name):
             print(f"[!] Temp file disappeared: {temp_name}")

        res = service.predict_video(temp_name)

        print(f"[*] Analiz bitti. Skor: {res['violence_prob']}")
        async with httpx.AsyncClient() as client:
            await client.patch(
                f"{NODE_BACKEND_URL}/{video_id}",
                json={
                    "isAnomaly": bool(res["is_violence"]),
                    "accuracy": round(float(res["violence_prob"]) * 100, 2)
                }
            )
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[!] Hata: {str(e)}")
    finally:
        if os.path.exists(temp_name):
            os.remove(temp_name)
            print(f"[*] Gecici dosya silindi: {temp_name}")

@app.post("/analyze")
async def analyze(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(perform_analysis, req.id, req.videoUrl)
    return {"message": "Started", "id": req.id}