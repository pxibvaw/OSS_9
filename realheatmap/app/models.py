# models.py
from sqlalchemy import Column, Integer, Float, String, DateTime
from realheatmap.app.database import Base
from datetime import datetime

class WeatherRaw(Base):
    __tablename__ = "weather_raw"
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, index=True)               # 자치구 이름
    temperature = Column(Float, nullable=True)        # 기온
    humidity = Column(Float, nullable=True)           # 습도
    wind = Column(Float, nullable=True)               # 풍속
    timestamp = Column(DateTime, default=datetime.utcnow)  # 수집 시각

class WeatherCalculated(Base):
    __tablename__ = "weather_calculated"
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, index=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    wind = Column(Float, nullable=True)
    effective_humidity = Column(Float, nullable=True)        # 실효습도
    timestamp = Column(DateTime, default=datetime.utcnow)

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