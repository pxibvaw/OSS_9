document.addEventListener("DOMContentLoaded", () => {
  const districtButton = document.querySelectorAll('.header-button')[0];
  const weatherButton = document.querySelectorAll('.header-button')[1];

  const districtView = document.getElementById('district-risk-view');
  const weatherView = document.getElementById('weather-risk-view');
  const region_nameElem = document.getElementById('selected-district-name');

  // 자치구 선택 초기화 함수
  function resetSelectedDistrict() {
    // 지도 선택 효과 제거
    document.querySelectorAll("g.selected-gu").forEach(el => {
      el.classList.remove("selected-gu");
    });

    // 자치구 이름 초기화 (모든 화면)
    document.querySelectorAll("#selected-district-name").forEach(el => {
      el.textContent = "자치구 선택";
    });

    // 위험지수 초기화
    const riskEl = document.getElementById("risk-score-value");
    if (riskEl) riskEl.textContent = "-- %";

    // 탐지 위험 요소 초기화
    const dangerIds = ["cigarette-count", "wires-count", "smoke-count", "garbage-count"];
    dangerIds.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.textContent = "0";
    });

    // 기상 정보 초기화
    const weatherIds = ["risk-score", "Tmean", "Rh", "Eh", "Wmean", "daily-weight", "model-type", "model-formula"];
    weatherIds.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.textContent = "-";
    });
  }

  // 버튼 클릭 시 화면 전환 + 초기화
  districtButton.addEventListener('click', () => {
    districtView.style.display = 'flex';
    weatherView.style.display = 'none';
    resetSelectedDistrict();  // 초기화
  });

  weatherButton.addEventListener('click', () => {
    districtView.style.display = 'none';
    weatherView.style.display = 'flex';
    resetSelectedDistrict();  // 초기화
  });

  // 지도에서 자치구 클릭 이벤트 처리
  const guElements = document.querySelectorAll("svg g");

  guElements.forEach(gu => {
    gu.addEventListener("click", () => {
      // 기존 선택 해제
      document.querySelectorAll("g.selected-gu").forEach(el => {
        el.classList.remove("selected-gu");
      });
      gu.classList.add("selected-gu");

      const label = gu.querySelector(".label");
      const region_name = label ? label.textContent.trim() : gu.id;

      // 사이드 패널 자치구명 갱신
      region_nameElem.textContent = region_name;

      // 현재 보이는 화면에 따라 처리
      if (districtView && districtView.style.display !== "none") {
        districtView.querySelector("#selected-district-name").textContent = region_name;
        loadRiskScore(region_name);  // 위험지수 로드
      }

      if (weatherView && weatherView.style.display !== "none") {
        weatherView.querySelector("#selected-district-name").textContent = region_name;
        loadWeatherData(region_name);  // 기상정보 로드
      }
    });
  });
});

// 위험지수 및 탐지요소 불러오기
function loadRiskScore(region_name) {
  fetch(`http://localhost:8000/risk?region=${encodeURIComponent(region_name)}`)
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

// 기상정보 기반 위험도 불러오기
function loadWeatherData(region_name) {
  fetch(`http://localhost:8000/weather-info?region=${encodeURIComponent(region_name)}`)
    .then(res => res.json())
    .then(data => {
      document.getElementById('risk-score').textContent = `${data.risk_score} 등급`;
      document.getElementById('Tmean').textContent = `${data.temperature} ℃`;
      document.getElementById('Rh').textContent = `${data.humidity} %`;
      document.getElementById('Eh').textContent = `${data.real_feel_humidity} %`;
      document.getElementById('Wmean').textContent = `${data.wind} m/s`;
      document.getElementById('daily-weight').textContent = data.daily_weight;

      // 계절에 따른 모델 정보 표시
      const month = parseInt(data.date.split('-')[1]);
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
