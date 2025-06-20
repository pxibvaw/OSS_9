from sqlalchemy import Column, Integer, Float, String, DateTime, Date
from realheatmap.app.database.database import Base 
from datetime import datetime

class WeatherRaw(Base):
    __tablename__ = "weather_raw"
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, index=True)               # 자치구 이름
    district_id = Column(Integer, index=True)         # ✅ 자치구 ID
    date = Column(Date, index=True)                   # ✅ 측정 날짜 (YYYY-MM-DD)
    temperature = Column(Float, nullable=True)        # 기온
    humidity = Column(Float, nullable=True)           # 습도
    wind = Column(Float, nullable=True)               # 풍속
    timestamp = Column(DateTime, default=datetime.utcnow)  # 수집 시각

class WeatherCalculated(Base):
    __tablename__ = "weather_calculated"

    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, index=True)                 # 자치구 이름
    district_id = Column(Integer, index=True, nullable=True)  # 사용 안 하므로 nullable 처리
    date = Column(Date, index=True)                     # 기준 날짜 (실효습도 계산 기준)
    temperature = Column(Float, nullable=True)          # 해당 날짜의 기온
    humidity = Column(Float, nullable=True)             # 해당 날짜의 습도
    wind = Column(Float, nullable=True)                 # 해당 날짜의 풍속
    effective_humidity = Column(Float, nullable=True)   # 실효습도
    timestamp = Column(DateTime, default=datetime.utcnow)  # 저장 시점 또는 원본 시간

class FireRiskScore(Base):
    __tablename__ = "fire_risk_score"
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, index=True)
    score_type = Column(String)      # 예: 'tmp_score', 'risk_score'
    score_value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class BaseIndicator(Base):
    __tablename__ = "base_indicators"
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, index=True)
    indicator_name = Column(String)     # 예: '재정자주도', '노후건축물 비율' 등
    indicator_value = Column(Float)
    
class ObjectDetection(Base):
    __tablename__ = "object_detection"

    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, index=True)         # 자치구 이름
    cigarettes = Column(Integer, default=0)     # class 0
    garbage = Column(Integer, default=0)        # class 1
    smoke = Column(Integer, default=0)          # class 2
    wires = Column(Integer, default=0)          # class 3
    timestamp = Column(DateTime, default=datetime.utcnow)  # 수집 시각