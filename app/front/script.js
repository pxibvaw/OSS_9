document.addEventListener("DOMContentLoaded", () => {
  const districtButton = document.querySelectorAll('.header-button')[0];
  const weatherButton = document.querySelectorAll('.header-button')[1];

  const districtView = document.getElementById('district-risk-view');
  const weatherView = document.getElementById('weather-risk-view');
  const region_nameElem = document.getElementById('selected-district-name');

  function resetSelectedDistrict() {
    document.querySelectorAll("g.selected-gu").forEach(el => {
      el.classList.remove("selected-gu");
    });

    document.querySelectorAll("#selected-district-name").forEach(el => {
      el.textContent = "자치구 선택";
    });

    const riskEl = document.getElementById("risk-score-value");
    if (riskEl) riskEl.textContent = "-- %";

    const dangerIds = ["cigarette-count", "wires-count", "smoke-count", "garbage-count"];
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
    gu.addEventListener("click", () => {
      document.querySelectorAll("g.selected-gu").forEach(el => {
        el.classList.remove("selected-gu");
      });
      gu.classList.add("selected-gu");

      const label = gu.querySelector(".label");
      const region_name = label ? label.textContent.trim() : gu.id;
      region_nameElem.textContent = region_name;
      sendRegionNameToBackend(region_name);

      if (districtView && districtView.style.display !== "none") {
        districtView.querySelector("#selected-district-name").textContent = region_name;
        loadRiskScore(region_name);
      }

      if (weatherView && weatherView.style.display !== "none") {
        weatherView.querySelector("#selected-district-name").textContent = region_name;
        loadWeatherData(region_name);
      }
    });
  });
});

function loadRiskScore(region_name) {
  fetch(`/base-risk?region=${encodeURIComponent(region_name)}`)
    .then(response => response.json())
    .then(data => {
      document.getElementById("risk-score-value").textContent = `${data.total_score} %`;

      const danger = data.danger_elements || {};
      document.getElementById("cigarette-count").textContent = danger.cigarette ?? 0;
      document.getElementById("wires-count").textContent = danger.wires ?? 0;
      document.getElementById("smoke-count").textContent = danger.smoke ?? 0;
      document.getElementById("garbage-count").textContent = danger.garbage ?? 0;
    })
    .catch(err => {
      console.error("위험지수 가져오기 실패", err);
      document.getElementById("risk-score-value").textContent = "-- %";
      ["cigarette-count", "wires-count", "smoke-count", "garbage-count"].forEach(id => {
        document.getElementById(id).textContent = "0";
      });
    });
}

function loadWeatherData(region_name) {
  const today = new Date().toISOString().split("T")[0];

  Promise.all([
    fetch(`/weather-info?region=${encodeURIComponent(region_name)}`).then(res => res.json()),
    fetch(`/humidity/${encodeURIComponent(region_name)}?date=${today}`).then(res => res.json()),
    fetch(`/calculate-risk?region=${encodeURIComponent(region_name)}&date=${today}`).then(res => res.json())
  ])
    .then(([weather, humidity, risk]) => {
      document.getElementById('Tmean').textContent = `${weather.temperature} ℃`;
      document.getElementById('Rh').textContent = `${weather.humidity} %`;
      document.getElementById('Eh').textContent = `${humidity.effective_humidity} %`;
      document.getElementById('Wmean').textContent = `${weather.wind} m/s`;
      document.getElementById('daily-weight').textContent = risk.daily_weight ?? '-';

      document.getElementById('risk-score').textContent = `${risk.risk_score} 등급`;

      const month = parseInt(today.split('-')[1]);
      const model = (1 <= month && month <= 6) ? "봄철 모델" : "가을 모델";
      document.getElementById('model-type').textContent = model;

      const formula = model === "봄철 모델"
        ? `risk = 1 / (1 + exp(-(2.706 + 0.088*Tmean - 0.055*Rh - 0.023*Eh - 0.014*Wmean))) - 1`
        : `risk = 1 / (1 + exp(-(1.099 + 0.117*Tmean - 0.069*Rh - 0.182*Wmean))) - 1`;

      document.getElementById('model-formula').textContent = formula;
    })
    .catch(error => {
      console.error('기상 데이터 오류:', error);
    });
}

function sendRegionNameToBackend(region_name) {
  fetch('/receive-region', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ region: region_name })
  })
    .then(res => res.json())
    .then(data => {
      console.log("백엔드 응답:", data);
    })
    .catch(err => {
      console.error("구 이름 전송 실패:", err);
    });
}