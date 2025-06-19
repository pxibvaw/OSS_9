from sqlalchemy import create_engine, text

# SQLite 연결
engine = create_engine("sqlite:///./fire_risk.db")

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT id, region, temperature, humidity, wind, timestamp
        FROM weather_raw
        ORDER BY timestamp DESC
        LIMIT 30;
    """))

    print("✅ weather_raw 테이블 최근 데이터:")
    for row in result:
        print(f"[{row.region}] {row.timestamp} | T: {row.temperature}°C | H: {row.humidity}% | W: {row.wind}m/s")