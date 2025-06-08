// 버튼 가져오기
const districtButton = document.querySelectorAll('.header-button')[0];
const weatherButton = document.querySelectorAll('.header-button')[1];

// 화면 섹션 가져오기
const districtView = document.getElementById('district-risk-view');
const weatherView = document.getElementById('weather-risk-view');

// 클릭 이벤트 설정
districtButton.addEventListener('click', () => {
  districtView.style.display = 'flex';
  weatherView.style.display = 'none';
});

weatherButton.addEventListener('click', () => {
  districtView.style.display = 'none';
  weatherView.style.display = 'flex';
});

function loadWeatherData(districtName) {
  fetch(`http://localhost:8000/weather?district=${encodeURIComponent(districtName)}`)
    .then(response => {
      if (!response.ok) throw new Error('데이터 불러오기 실패');
      return response.json();
    })
    .then(data => {
      document.getElementById('wind-speed').textContent = `${data.wind_speed} m/s`;
      document.getElementById('temperature').textContent = `${data.temperature} ℃`;
      document.getElementById('humidity').textContent = `${data.humidity} %`;
      document.getElementById('real-feel-humidity').textContent = `${data.real_feel_humidity} %`;
    })
    .catch(error => {
      console.error('기상 데이터 오류:', error);
    });
}
