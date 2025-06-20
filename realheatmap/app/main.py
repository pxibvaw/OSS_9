from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel

class RegionRequest(BaseModel):
    region: str

# DB
from realheatmap.app.database.database import engine
from realheatmap.app.database import models
models.Base.metadata.create_all(bind=engine)

# 라우터
from realheatmap.app.api.weather_api import router as weather_router
from realheatmap.app.api.humidity_api import router as humidity_router
from realheatmap.app.api.risk_api import router as risk_router

# 프론트 연결 경로
BASE_DIR = Path(__file__).resolve().parent
FRONT_DIR = BASE_DIR / "front"

# FastAPI 앱 생성
app = FastAPI()

# API 라우터 등록
app.include_router(weather_router)
app.include_router(humidity_router)
app.include_router(risk_router)

# 정적 파일 제공 (JS, CSS, 이미지 등)
app.mount("/static", StaticFiles(directory=str(FRONT_DIR)), name="static")

# 기본 index.html 페이지 제공
@app.get("/")
def serve_front():
    return FileResponse(str(FRONT_DIR / "index.html"))

@app.post("/receive-region")
async def receive_region(data: RegionRequest):
    print(f"프론트로부터 받은 구 이름: {data.region}")
    return {"message": f"{data.region} 정상 수신"}