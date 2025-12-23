import cv2
import numpy as np
import requests
from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProcessRequest(BaseModel):
    image_url: str

def run_ai_model(img_array):
    try:

        processed = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        
        # Tekrar 3 kanala çevir ki renkli resim formatında kalsın (Opsiyonel)
        processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
        
        # Test için bir kutu çizelim (Anomali bulmuş gibi)
        h, w, _ = processed.shape
        cv2.rectangle(processed, (50, 50), (w-50, h-50), (0, 0, 255), 5)
        
        return processed
    except Exception as e:
        print(f"AI Model Hatası: {e}")
        raise e

# ---------------------------------------------------------
# ENDPOINT
# ---------------------------------------------------------
@app.post("/process")
async def process_image(request: ProcessRequest):
    try:
        # 1. ADIM: Resmi URL'den RAM'e İndir (Diske yazma yok)
        resp = requests.get(request.image_url, timeout=10)
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Resim indirilemedi.")
            
        # Byte dizisini OpenCV formatına çevir
        image_bytes = np.asarray(bytearray(resp.content), dtype="uint8")
        img = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

        # 2. ADIM: Yapay Zekayı Çalıştır
        result_img = run_ai_model(img)

        # 3. ADIM: Resmi RAM'de JPG formatına sıkıştır (Encode)
        # ret: Başarılı mı?, buffer: Resim verisi
        ret, buffer = cv2.imencode('.jpg', result_img)
        
        if not ret:
            raise HTTPException(status_code=500, detail="Resim encode edilemedi.")

        # 4. ADIM: Bayt verisini (buffer) direkt Express'e fırlat
        return Response(content=buffer.tobytes(), media_type="image/jpeg")

    except Exception as e:
        print(f"Sunucu Hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)