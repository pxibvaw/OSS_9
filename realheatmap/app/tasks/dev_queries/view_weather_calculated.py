from realheatmap.app.database.database import SessionLocal
from realheatmap.app.database.models import WeatherCalculated

def view_all_weather_calculated():
    db = SessionLocal()
    try:
        rows = db.query(WeatherCalculated).all()
        for r in rows:
            print(
                f"[{r.region}] {r.date} | T: {r.temperature}°C | H: {r.humidity}% | W: {r.wind}m/s | He: {r.effective_humidity}"
            )
    finally:
        db.close()

if __name__ == "__main__":
    view_all_weather_calculated()