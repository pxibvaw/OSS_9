document.addEventListener("DOMContentLoaded", () => {
  const districtButton = document.querySelectorAll('.header-button')[0];
  const weatherButton = document.querySelectorAll('.header-button')[1];

  const districtView = document.getElementById('district-risk-view');
  const weatherView = document.getElementById('weather-risk-view');
  const region_nameElem = document.getElementById('selected-district-name');

  function resetSelectedDistrict() {
    document.querySelectorAll("g.selected-gu").forEach(el => el.classList.remove("selected-gu"));
    document.querySelectorAll("#selected-district-name").forEach(el => el.textContent = "자치구 선택");

    const riskEl = document.getElementById("risk-score-value");
    if (riskEl) riskEl.textContent = "-- %";

    const dangerIds = ["cigarette", "wires", "smoke", "garbage"];
    dangerIds.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.textContent = "0";
    });

    const weatherIds = ["risk-score", "Tmean", "Rh", "Eh", "Wmean", "daily-weight", "model-type", "model-formula"];
    weatherIds.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.textContent = "-";
    });
  }

  districtButton.addEventListener('click', () => {
    districtView.style.display = 'flex';
    weatherView.style.display = 'none';
    resetSelectedDistrict();
  });

  weatherButton.addEventListener('click', () => {
    districtView.style.display = 'none';
    weatherView.style.display = 'flex';
    resetSelectedDistrict();
  });

  const guElements = document.querySelectorAll("svg g");

  guElements.forEach(gu => {
    gu.addEventListener("click", async () => {
      document.querySelectorAll("g.selected-gu").forEach(el => el.classList.remove("selected-gu"));
      gu.classList.add("selected-gu");

      const label = gu.querySelector(".label");
      const region_name = label ? label.textContent.trim() : gu.id;
      region_nameElem.textContent = region_name;

      await sendRegionNameToBackend(region_name);

      if (districtView && districtView.style.display !== "none") {
        districtView.querySelector("#selected-district-name").textContent = region_name;
        await loadRiskScore(region_name);
      }

      if (weatherView && weatherView.style.display !== "none") {
        weatherView.querySelector("#selected-district-name").textContent = region_name;
        await loadWeatherData(region_name);
      }
    });
  });
});

async function loadRiskScore(region_name) {
  try {
    const response = await fetch(`/base-risk?region=${encodeURIComponent(region_name)}`);
    const data = await response.json();

    document.getElementById("risk-score-value").textContent = `${data.total_score} %`;

    const danger = data.danger_elements || {};
      document.getElementById("cigarette").textContent = danger.cigarette ?? 0;
      document.getElementById("wires").textContent = danger.wires ?? 0;
      document.getElementById("smoke").textContent = danger.smoke ?? 0;
      document.getElementById("garbage").textContent = danger.garbage ?? 0;

  } catch (err) {
    console.error("위험지수 가져오기 실패", err);
    document.getElementById("risk-score-value").textContent = "-- %";
    ["cigarette", "wires", "smoke", "garbage"].forEach(id => {
      document.getElementById(id).textContent = "0";
    });
  }
}

async function loadWeatherData(region_name) {
  const today = new Date().toISOString().split("T")[0];

  try {
    const [weather, humidity, risk] = await Promise.all([
      fetch(`/weather-info?region=${encodeURIComponent(region_name)}`).then(res => res.json()),
      fetch(`/humidity/${encodeURIComponent(region_name)}?date=${today}`).then(res => res.json()),
      fetch(`/calculate-risk?region=${encodeURIComponent(region_name)}&date=${today}`).then(res => res.json())
    ]);

    const temp = Number(weather.temperature).toFixed(1);
    const hum = Number(weather.humidity).toFixed(1);
    const eh = Number(humidity.effective_humidity).toFixed(1);
    const wind = Number(weather.wind).toFixed(1);
    const score = risk.risk_score ?? '-';
    const weight = risk.daily_weight ?? '-';

    document.getElementById('Tmean').textContent = `${temp} ℃`;
    document.getElementById('Rh').textContent = `${hum} %`;
    document.getElementById('eh').textContent = `${eh} %`;
    document.getElementById('Wmean').textContent = `${wind} m/s`;
    document.getElementById('daily-weight').textContent = weight;
    document.getElementById('risk-score').textContent = `${score} 등급`;

    const month = parseInt(today.split('-')[1]);
    const model = (1 <= month && month <= 6) ? "봄철 모델" : "가을 모델";
    document.getElementById('model-type').textContent = model;

    const formula = model === "봄철 모델"
      ? `risk = 1 / (1 + exp(-(2.706 + 0.088*Tmean - 0.055*Rh - 0.023*Eh - 0.014*Wmean))) - 1`
      : `risk = 1 / (1 + exp(-(1.099 + 0.117*Tmean - 0.069*Rh - 0.182*Wmean))) - 1`;
    document.getElementById('model-formula').textContent = formula;

  } catch (error) {
    console.error('기상 데이터 오류:', error);
  }
}

async function sendRegionNameToBackend(region_name) {
  try {
    const response = await fetch('/receive-region', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ region: region_name })
    });
    const data = await response.json();
    console.log("백엔드 응답:", data);
  } catch (err) {
    console.error("구 이름 전송 실패:", err);
  }
}